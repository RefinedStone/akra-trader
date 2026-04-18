from __future__ import annotations

import json
import logging
from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Callable
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.ports import OperatorAlertDeliveryPort


LOGGER = logging.getLogger("akra_trader.operator_delivery")


def _normalize_target(target: str) -> str | None:
  normalized = target.strip().lower().replace("-", "_")
  if not normalized:
    return None
  if normalized in {"console", "operator_console"}:
    return "operator_console"
  if normalized in {"webhook", "operator_webhook"}:
    return "operator_webhook"
  if normalized in {"slack", "slack_webhook", "operator_slack"}:
    return "slack_webhook"
  if normalized in {"pagerduty", "pagerduty_events", "operator_pagerduty"}:
    return "pagerduty_events"
  if normalized in {"incidentio", "incident_io", "incidentio_incidents", "operator_incidentio"}:
    return "incidentio_incidents"
  if normalized in {"firehydrant", "fire_hydrant", "firehydrant_incidents", "operator_firehydrant"}:
    return "firehydrant_incidents"
  if normalized in {"rootly", "root_ly", "rootly_incidents", "operator_rootly"}:
    return "rootly_incidents"
  if normalized in {"blameless", "blameless_incidents", "operator_blameless"}:
    return "blameless_incidents"
  if normalized in {"xmatters", "x_matters", "xmatters_incidents", "operator_xmatters"}:
    return "xmatters_incidents"
  if normalized in {"servicenow", "service_now", "servicenow_incidents", "operator_servicenow"}:
    return "servicenow_incidents"
  if normalized in {"squadcast", "squad_cast", "squadcast_incidents", "operator_squadcast"}:
    return "squadcast_incidents"
  if normalized in {"bigpanda", "big_panda", "bigpanda_incidents", "operator_bigpanda"}:
    return "bigpanda_incidents"
  if normalized in {
    "grafanaoncall",
    "grafana_oncall",
    "grafana_oncall_incidents",
    "operator_grafana_oncall",
  }:
    return "grafana_oncall_incidents"
  if normalized in {"zenduty", "zen_duty", "zenduty_incidents", "operator_zenduty"}:
    return "zenduty_incidents"
  if normalized in {
    "splunk_oncall",
    "splunkoncall",
    "splunk_oncall_incidents",
    "victorops",
    "operator_splunk_oncall",
  }:
    return "splunk_oncall_incidents"
  if normalized in {
    "jira_service_management",
    "jira_service_management_incidents",
    "jsm",
    "jsm_incidents",
    "jira_service_desk",
    "jira_service_desk_incidents",
    "operator_jira_service_management",
  }:
    return "jira_service_management_incidents"
  if normalized in {"pagertree", "pager_tree", "pagertree_incidents", "operator_pagertree"}:
    return "pagertree_incidents"
  if normalized in {"alertops", "alert_ops", "alertops_incidents", "operator_alertops"}:
    return "alertops_incidents"
  if normalized in {"signl4", "signl_4", "signl4_incidents", "operator_signl4"}:
    return "signl4_incidents"
  if normalized in {"ilert", "i_lert", "ilert_incidents", "ilert_alerts", "operator_ilert"}:
    return "ilert_incidents"
  if normalized in {
    "betterstack",
    "better_stack",
    "betterstack_incidents",
    "betterstack_alerts",
    "operator_betterstack",
  }:
    return "betterstack_incidents"
  if normalized in {"onpage", "on_page", "onpage_incidents", "onpage_alerts", "operator_onpage"}:
    return "onpage_incidents"
  if normalized in {"allquiet", "all_quiet", "allquiet_incidents", "allquiet_alerts", "operator_allquiet"}:
    return "allquiet_incidents"
  if normalized in {"moogsoft", "moogsoft_incidents", "moogsoft_alerts", "operator_moogsoft"}:
    return "moogsoft_incidents"
  if normalized in {"spikesh", "spike_sh", "spikesh_incidents", "spikesh_alerts", "operator_spikesh"}:
    return "spikesh_incidents"
  if normalized in {"dutycalls", "duty_calls", "dutycalls_incidents", "dutycalls_alerts", "operator_dutycalls"}:
    return "dutycalls_incidents"
  if normalized in {"incidenthub", "incident_hub", "incidenthub_incidents", "incidenthub_alerts", "operator_incidenthub"}:
    return "incidenthub_incidents"
  if normalized in {"resolver", "resolver_incidents", "resolver_alerts", "operator_resolver"}:
    return "resolver_incidents"
  if normalized in {"openduty", "open_duty", "openduty_incidents", "openduty_alerts", "operator_openduty"}:
    return "openduty_incidents"
  if normalized in {"cabot", "cabot_incidents", "cabot_alerts", "operator_cabot"}:
    return "cabot_incidents"
  if normalized in {"haloitsm", "halo_itsm", "haloitsm_incidents", "haloitsm_alerts", "operator_haloitsm"}:
    return "haloitsm_incidents"
  if normalized in {
    "incidentmanagerio",
    "incidentmanager_io",
    "incidentmanagerio_incidents",
    "incidentmanagerio_alerts",
    "operator_incidentmanagerio",
  }:
    return "incidentmanagerio_incidents"
  if normalized in {"oneuptime", "one_uptime", "oneuptime_incidents", "oneuptime_alerts", "operator_oneuptime"}:
    return "oneuptime_incidents"
  if normalized in {"squzy", "squzy_incidents", "squzy_alerts", "operator_squzy"}:
    return "squzy_incidents"
  if normalized in {"opsramp", "ops_ramp", "opsramp_incidents", "opsramp_alerts", "operator_opsramp"}:
    return "opsramp_incidents"
  if normalized in {"opsgenie", "opsgenie_alerts", "operator_opsgenie"}:
    return "opsgenie_alerts"
  return None


class OperatorAlertDeliveryAdapter(OperatorAlertDeliveryPort):
  def __init__(
    self,
    *,
    targets: tuple[str, ...] = ("console",),
    webhook_url: str | None = None,
    slack_webhook_url: str | None = None,
    pagerduty_integration_key: str | None = None,
    pagerduty_api_token: str | None = None,
    pagerduty_from_email: str | None = None,
    pagerduty_recovery_engine_url_template: str | None = None,
    pagerduty_recovery_engine_token: str | None = None,
    incidentio_api_token: str | None = None,
    incidentio_api_url: str = "https://api.incident.io",
    incidentio_recovery_engine_url_template: str | None = None,
    incidentio_recovery_engine_token: str | None = None,
    firehydrant_api_token: str | None = None,
    firehydrant_api_url: str = "https://api.firehydrant.io",
    firehydrant_recovery_engine_url_template: str | None = None,
    firehydrant_recovery_engine_token: str | None = None,
    rootly_api_token: str | None = None,
    rootly_api_url: str = "https://api.rootly.com",
    rootly_recovery_engine_url_template: str | None = None,
    rootly_recovery_engine_token: str | None = None,
    blameless_api_token: str | None = None,
    blameless_api_url: str = "https://api.blameless.com",
    blameless_recovery_engine_url_template: str | None = None,
    blameless_recovery_engine_token: str | None = None,
    xmatters_api_token: str | None = None,
    xmatters_api_url: str = "https://api.xmatters.com",
    xmatters_recovery_engine_url_template: str | None = None,
    xmatters_recovery_engine_token: str | None = None,
    servicenow_api_token: str | None = None,
    servicenow_api_url: str = "https://api.servicenow.com",
    servicenow_recovery_engine_url_template: str | None = None,
    servicenow_recovery_engine_token: str | None = None,
    squadcast_api_token: str | None = None,
    squadcast_api_url: str = "https://api.squadcast.com",
    squadcast_recovery_engine_url_template: str | None = None,
    squadcast_recovery_engine_token: str | None = None,
    bigpanda_api_token: str | None = None,
    bigpanda_api_url: str = "https://api.bigpanda.io",
    bigpanda_recovery_engine_url_template: str | None = None,
    bigpanda_recovery_engine_token: str | None = None,
    grafana_oncall_api_token: str | None = None,
    grafana_oncall_api_url: str = "https://oncall-api.grafana.com",
    grafana_oncall_recovery_engine_url_template: str | None = None,
    grafana_oncall_recovery_engine_token: str | None = None,
    zenduty_api_token: str | None = None,
    zenduty_api_url: str = "https://api.zenduty.com",
    zenduty_recovery_engine_url_template: str | None = None,
    zenduty_recovery_engine_token: str | None = None,
    splunk_oncall_api_token: str | None = None,
    splunk_oncall_api_url: str = "https://api.splunkoncall.com",
    splunk_oncall_recovery_engine_url_template: str | None = None,
    splunk_oncall_recovery_engine_token: str | None = None,
    jira_service_management_api_token: str | None = None,
    jira_service_management_api_url: str = "https://api.atlassian.com/jsm",
    jira_service_management_recovery_engine_url_template: str | None = None,
    jira_service_management_recovery_engine_token: str | None = None,
    pagertree_api_token: str | None = None,
    pagertree_api_url: str = "https://api.pagertree.com",
    pagertree_recovery_engine_url_template: str | None = None,
    pagertree_recovery_engine_token: str | None = None,
    alertops_api_token: str | None = None,
    alertops_api_url: str = "https://api.alertops.com",
    alertops_recovery_engine_url_template: str | None = None,
    alertops_recovery_engine_token: str | None = None,
    signl4_api_token: str | None = None,
    signl4_api_url: str = "https://connect.signl4.com",
    signl4_recovery_engine_url_template: str | None = None,
    signl4_recovery_engine_token: str | None = None,
    ilert_api_token: str | None = None,
    ilert_api_url: str = "https://api.ilert.com",
    ilert_recovery_engine_url_template: str | None = None,
    ilert_recovery_engine_token: str | None = None,
    betterstack_api_token: str | None = None,
    betterstack_api_url: str = "https://uptime.betterstack.com/api/v2",
    betterstack_recovery_engine_url_template: str | None = None,
    betterstack_recovery_engine_token: str | None = None,
    onpage_api_token: str | None = None,
    onpage_api_url: str = "https://api.onpage.com/v1",
    onpage_recovery_engine_url_template: str | None = None,
    onpage_recovery_engine_token: str | None = None,
    allquiet_api_token: str | None = None,
    allquiet_api_url: str = "https://api.allquiet.app/v1",
    allquiet_recovery_engine_url_template: str | None = None,
    allquiet_recovery_engine_token: str | None = None,
    moogsoft_api_token: str | None = None,
    moogsoft_api_url: str = "https://api.moogsoft.com/v1",
    moogsoft_recovery_engine_url_template: str | None = None,
    moogsoft_recovery_engine_token: str | None = None,
    spikesh_api_token: str | None = None,
    spikesh_api_url: str = "https://api.spike.sh/v1",
    spikesh_recovery_engine_url_template: str | None = None,
    spikesh_recovery_engine_token: str | None = None,
    dutycalls_api_token: str | None = None,
    dutycalls_api_url: str = "https://api.dutycalls.com/v1",
    dutycalls_recovery_engine_url_template: str | None = None,
    dutycalls_recovery_engine_token: str | None = None,
    incidenthub_api_token: str | None = None,
    incidenthub_api_url: str = "https://api.incidenthub.cloud/v1",
    incidenthub_recovery_engine_url_template: str | None = None,
    incidenthub_recovery_engine_token: str | None = None,
    resolver_api_token: str | None = None,
    resolver_api_url: str = "https://api.resolver.com/v1",
    resolver_recovery_engine_url_template: str | None = None,
    resolver_recovery_engine_token: str | None = None,
    openduty_api_token: str | None = None,
    openduty_api_url: str = "https://api.openduty.com/v1",
    openduty_recovery_engine_url_template: str | None = None,
    openduty_recovery_engine_token: str | None = None,
    cabot_api_token: str | None = None,
    cabot_api_url: str = "https://api.cabot.io/v1",
    cabot_recovery_engine_url_template: str | None = None,
    cabot_recovery_engine_token: str | None = None,
    haloitsm_api_token: str | None = None,
    haloitsm_api_url: str = "https://api.haloitsm.com/v1",
    haloitsm_recovery_engine_url_template: str | None = None,
    haloitsm_recovery_engine_token: str | None = None,
    incidentmanagerio_api_token: str | None = None,
    incidentmanagerio_api_url: str = "https://api.incidentmanager.io/v1",
    incidentmanagerio_recovery_engine_url_template: str | None = None,
    incidentmanagerio_recovery_engine_token: str | None = None,
    oneuptime_api_token: str | None = None,
    oneuptime_api_url: str = "https://api.oneuptime.com/v1",
    oneuptime_recovery_engine_url_template: str | None = None,
    oneuptime_recovery_engine_token: str | None = None,
    squzy_api_token: str | None = None,
    squzy_api_url: str = "https://api.squzy.app/v1",
    squzy_recovery_engine_url_template: str | None = None,
    squzy_recovery_engine_token: str | None = None,
    opsramp_api_token: str | None = None,
    opsramp_api_url: str = "https://api.opsramp.com/v1",
    opsramp_recovery_engine_url_template: str | None = None,
    opsramp_recovery_engine_token: str | None = None,
    opsgenie_api_key: str | None = None,
    opsgenie_api_url: str = "https://api.opsgenie.com",
    opsgenie_recovery_engine_url_template: str | None = None,
    opsgenie_recovery_engine_api_key: str | None = None,
    webhook_timeout_seconds: int = 5,
    clock: Callable[[], datetime] | None = None,
    urlopen: Callable[..., object] | None = None,
  ) -> None:
    normalized_targets = []
    for target in targets:
      normalized = _normalize_target(target)
      if normalized is not None and normalized not in normalized_targets:
        normalized_targets.append(normalized)
    self._targets = tuple(normalized_targets)
    self._webhook_url = webhook_url
    self._slack_webhook_url = slack_webhook_url
    self._pagerduty_integration_key = pagerduty_integration_key
    self._pagerduty_api_token = pagerduty_api_token
    self._pagerduty_from_email = pagerduty_from_email
    self._pagerduty_recovery_engine_url_template = pagerduty_recovery_engine_url_template
    self._pagerduty_recovery_engine_token = pagerduty_recovery_engine_token
    self._incidentio_api_token = incidentio_api_token
    self._incidentio_api_url = incidentio_api_url.rstrip("/")
    self._incidentio_recovery_engine_url_template = incidentio_recovery_engine_url_template
    self._incidentio_recovery_engine_token = incidentio_recovery_engine_token
    self._firehydrant_api_token = firehydrant_api_token
    self._firehydrant_api_url = firehydrant_api_url.rstrip("/")
    self._firehydrant_recovery_engine_url_template = firehydrant_recovery_engine_url_template
    self._firehydrant_recovery_engine_token = firehydrant_recovery_engine_token
    self._rootly_api_token = rootly_api_token
    self._rootly_api_url = rootly_api_url.rstrip("/")
    self._rootly_recovery_engine_url_template = rootly_recovery_engine_url_template
    self._rootly_recovery_engine_token = rootly_recovery_engine_token
    self._blameless_api_token = blameless_api_token
    self._blameless_api_url = blameless_api_url.rstrip("/")
    self._blameless_recovery_engine_url_template = blameless_recovery_engine_url_template
    self._blameless_recovery_engine_token = blameless_recovery_engine_token
    self._xmatters_api_token = xmatters_api_token
    self._xmatters_api_url = xmatters_api_url.rstrip("/")
    self._xmatters_recovery_engine_url_template = xmatters_recovery_engine_url_template
    self._xmatters_recovery_engine_token = xmatters_recovery_engine_token
    self._servicenow_api_token = servicenow_api_token
    self._servicenow_api_url = servicenow_api_url.rstrip("/")
    self._servicenow_recovery_engine_url_template = servicenow_recovery_engine_url_template
    self._servicenow_recovery_engine_token = servicenow_recovery_engine_token
    self._squadcast_api_token = squadcast_api_token
    self._squadcast_api_url = squadcast_api_url.rstrip("/")
    self._squadcast_recovery_engine_url_template = squadcast_recovery_engine_url_template
    self._squadcast_recovery_engine_token = squadcast_recovery_engine_token
    self._bigpanda_api_token = bigpanda_api_token
    self._bigpanda_api_url = bigpanda_api_url.rstrip("/")
    self._bigpanda_recovery_engine_url_template = bigpanda_recovery_engine_url_template
    self._bigpanda_recovery_engine_token = bigpanda_recovery_engine_token
    self._grafana_oncall_api_token = grafana_oncall_api_token
    self._grafana_oncall_api_url = grafana_oncall_api_url.rstrip("/")
    self._grafana_oncall_recovery_engine_url_template = grafana_oncall_recovery_engine_url_template
    self._grafana_oncall_recovery_engine_token = grafana_oncall_recovery_engine_token
    self._zenduty_api_token = zenduty_api_token
    self._zenduty_api_url = zenduty_api_url.rstrip("/")
    self._zenduty_recovery_engine_url_template = zenduty_recovery_engine_url_template
    self._zenduty_recovery_engine_token = zenduty_recovery_engine_token
    self._splunk_oncall_api_token = splunk_oncall_api_token
    self._splunk_oncall_api_url = splunk_oncall_api_url.rstrip("/")
    self._splunk_oncall_recovery_engine_url_template = splunk_oncall_recovery_engine_url_template
    self._splunk_oncall_recovery_engine_token = splunk_oncall_recovery_engine_token
    self._jira_service_management_api_token = jira_service_management_api_token
    self._jira_service_management_api_url = jira_service_management_api_url.rstrip("/")
    self._jira_service_management_recovery_engine_url_template = (
      jira_service_management_recovery_engine_url_template
    )
    self._jira_service_management_recovery_engine_token = (
      jira_service_management_recovery_engine_token
    )
    self._pagertree_api_token = pagertree_api_token
    self._pagertree_api_url = pagertree_api_url.rstrip("/")
    self._pagertree_recovery_engine_url_template = pagertree_recovery_engine_url_template
    self._pagertree_recovery_engine_token = pagertree_recovery_engine_token
    self._alertops_api_token = alertops_api_token
    self._alertops_api_url = alertops_api_url.rstrip("/")
    self._alertops_recovery_engine_url_template = alertops_recovery_engine_url_template
    self._alertops_recovery_engine_token = alertops_recovery_engine_token
    self._signl4_api_token = signl4_api_token
    self._signl4_api_url = signl4_api_url.rstrip("/")
    self._signl4_recovery_engine_url_template = signl4_recovery_engine_url_template
    self._signl4_recovery_engine_token = signl4_recovery_engine_token
    self._ilert_api_token = ilert_api_token
    self._ilert_api_url = ilert_api_url.rstrip("/")
    self._ilert_recovery_engine_url_template = ilert_recovery_engine_url_template
    self._ilert_recovery_engine_token = ilert_recovery_engine_token
    self._betterstack_api_token = betterstack_api_token
    self._betterstack_api_url = betterstack_api_url.rstrip("/")
    self._betterstack_recovery_engine_url_template = betterstack_recovery_engine_url_template
    self._betterstack_recovery_engine_token = betterstack_recovery_engine_token
    self._onpage_api_token = onpage_api_token
    self._onpage_api_url = onpage_api_url.rstrip("/")
    self._onpage_recovery_engine_url_template = onpage_recovery_engine_url_template
    self._onpage_recovery_engine_token = onpage_recovery_engine_token
    self._allquiet_api_token = allquiet_api_token
    self._allquiet_api_url = allquiet_api_url.rstrip("/")
    self._allquiet_recovery_engine_url_template = allquiet_recovery_engine_url_template
    self._allquiet_recovery_engine_token = allquiet_recovery_engine_token
    self._moogsoft_api_token = moogsoft_api_token
    self._moogsoft_api_url = moogsoft_api_url.rstrip("/")
    self._moogsoft_recovery_engine_url_template = moogsoft_recovery_engine_url_template
    self._moogsoft_recovery_engine_token = moogsoft_recovery_engine_token
    self._spikesh_api_token = spikesh_api_token
    self._spikesh_api_url = spikesh_api_url.rstrip("/")
    self._spikesh_recovery_engine_url_template = spikesh_recovery_engine_url_template
    self._spikesh_recovery_engine_token = spikesh_recovery_engine_token
    self._dutycalls_api_token = dutycalls_api_token
    self._dutycalls_api_url = dutycalls_api_url.rstrip("/")
    self._dutycalls_recovery_engine_url_template = dutycalls_recovery_engine_url_template
    self._dutycalls_recovery_engine_token = dutycalls_recovery_engine_token
    self._incidenthub_api_token = incidenthub_api_token
    self._incidenthub_api_url = incidenthub_api_url.rstrip("/")
    self._incidenthub_recovery_engine_url_template = incidenthub_recovery_engine_url_template
    self._incidenthub_recovery_engine_token = incidenthub_recovery_engine_token
    self._resolver_api_token = resolver_api_token
    self._resolver_api_url = resolver_api_url.rstrip("/")
    self._resolver_recovery_engine_url_template = resolver_recovery_engine_url_template
    self._resolver_recovery_engine_token = resolver_recovery_engine_token
    self._openduty_api_token = openduty_api_token
    self._openduty_api_url = openduty_api_url.rstrip("/")
    self._openduty_recovery_engine_url_template = openduty_recovery_engine_url_template
    self._openduty_recovery_engine_token = openduty_recovery_engine_token
    self._cabot_api_token = cabot_api_token
    self._cabot_api_url = cabot_api_url.rstrip("/")
    self._cabot_recovery_engine_url_template = cabot_recovery_engine_url_template
    self._cabot_recovery_engine_token = cabot_recovery_engine_token
    self._haloitsm_api_token = haloitsm_api_token
    self._haloitsm_api_url = haloitsm_api_url.rstrip("/")
    self._haloitsm_recovery_engine_url_template = haloitsm_recovery_engine_url_template
    self._haloitsm_recovery_engine_token = haloitsm_recovery_engine_token
    self._incidentmanagerio_api_token = incidentmanagerio_api_token
    self._incidentmanagerio_api_url = incidentmanagerio_api_url.rstrip("/")
    self._incidentmanagerio_recovery_engine_url_template = (
      incidentmanagerio_recovery_engine_url_template
    )
    self._incidentmanagerio_recovery_engine_token = incidentmanagerio_recovery_engine_token
    self._oneuptime_api_token = oneuptime_api_token
    self._oneuptime_api_url = oneuptime_api_url.rstrip("/")
    self._oneuptime_recovery_engine_url_template = oneuptime_recovery_engine_url_template
    self._oneuptime_recovery_engine_token = oneuptime_recovery_engine_token
    self._squzy_api_token = squzy_api_token
    self._squzy_api_url = squzy_api_url.rstrip("/")
    self._squzy_recovery_engine_url_template = squzy_recovery_engine_url_template
    self._squzy_recovery_engine_token = squzy_recovery_engine_token
    self._opsramp_api_token = opsramp_api_token
    self._opsramp_api_url = opsramp_api_url.rstrip("/")
    self._opsramp_recovery_engine_url_template = opsramp_recovery_engine_url_template
    self._opsramp_recovery_engine_token = opsramp_recovery_engine_token
    self._opsgenie_api_key = opsgenie_api_key
    self._opsgenie_api_url = opsgenie_api_url.rstrip("/")
    self._opsgenie_recovery_engine_url_template = opsgenie_recovery_engine_url_template
    self._opsgenie_recovery_engine_api_key = opsgenie_recovery_engine_api_key
    self._webhook_timeout_seconds = webhook_timeout_seconds
    self._clock = clock or (lambda: datetime.now(UTC))
    self._urlopen = urlopen or urllib_request.urlopen

  def list_targets(self) -> tuple[str, ...]:
    return self._targets

  def list_supported_workflow_providers(self) -> tuple[str, ...]:
    providers: list[str] = []
    if self._pagerduty_api_token and self._pagerduty_from_email:
      providers.append("pagerduty")
    if self._incidentio_api_token:
      providers.append("incidentio")
    if self._firehydrant_api_token:
      providers.append("firehydrant")
    if self._rootly_api_token:
      providers.append("rootly")
    if self._blameless_api_token:
      providers.append("blameless")
    if self._xmatters_api_token:
      providers.append("xmatters")
    if self._servicenow_api_token:
      providers.append("servicenow")
    if self._squadcast_api_token:
      providers.append("squadcast")
    if self._bigpanda_api_token:
      providers.append("bigpanda")
    if self._grafana_oncall_api_token:
      providers.append("grafana_oncall")
    if self._zenduty_api_token:
      providers.append("zenduty")
    if self._splunk_oncall_api_token:
      providers.append("splunk_oncall")
    if self._jira_service_management_api_token:
      providers.append("jira_service_management")
    if self._pagertree_api_token:
      providers.append("pagertree")
    if self._alertops_api_token:
      providers.append("alertops")
    if self._signl4_api_token:
      providers.append("signl4")
    if self._ilert_api_token:
      providers.append("ilert")
    if self._betterstack_api_token:
      providers.append("betterstack")
    if self._onpage_api_token:
      providers.append("onpage")
    if self._allquiet_api_token:
      providers.append("allquiet")
    if self._moogsoft_api_token:
      providers.append("moogsoft")
    if self._spikesh_api_token:
      providers.append("spikesh")
    if self._dutycalls_api_token:
      providers.append("dutycalls")
    if self._incidenthub_api_token:
      providers.append("incidenthub")
    if self._resolver_api_token:
      providers.append("resolver")
    if self._openduty_api_token:
      providers.append("openduty")
    if self._cabot_api_token:
      providers.append("cabot")
    if self._haloitsm_api_token:
      providers.append("haloitsm")
    if self._incidentmanagerio_api_token:
      providers.append("incidentmanagerio")
    if self._oneuptime_api_token:
      providers.append("oneuptime")
    if self._squzy_api_token:
      providers.append("squzy")
    if self._opsramp_api_token:
      providers.append("opsramp")
    if self._opsgenie_api_key:
      providers.append("opsgenie")
    return tuple(providers)

  def deliver(
    self,
    *,
    incident: OperatorIncidentEvent,
    targets: tuple[str, ...] | None = None,
    attempt_number: int = 1,
    phase: str = "initial",
  ) -> tuple[OperatorIncidentDelivery, ...]:
    records: list[OperatorIncidentDelivery] = []
    resolved_targets = targets or self._targets
    for target in resolved_targets:
      if target == "operator_console":
        records.append(self._deliver_console(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "operator_webhook":
        records.append(self._deliver_webhook(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "slack_webhook":
        records.append(self._deliver_slack(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "pagerduty_events":
        records.append(self._deliver_pagerduty(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "incidentio_incidents":
        records.append(self._deliver_incidentio(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "firehydrant_incidents":
        records.append(self._deliver_firehydrant(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "rootly_incidents":
        records.append(self._deliver_rootly(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "blameless_incidents":
        records.append(self._deliver_blameless(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "xmatters_incidents":
        records.append(self._deliver_xmatters(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "servicenow_incidents":
        records.append(self._deliver_servicenow(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "squadcast_incidents":
        records.append(self._deliver_squadcast(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "bigpanda_incidents":
        records.append(self._deliver_bigpanda(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "grafana_oncall_incidents":
        records.append(self._deliver_grafana_oncall(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "zenduty_incidents":
        records.append(self._deliver_zenduty(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "splunk_oncall_incidents":
        records.append(
          self._deliver_splunk_oncall(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "jira_service_management_incidents":
        records.append(
          self._deliver_jira_service_management(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "pagertree_incidents":
        records.append(
          self._deliver_pagertree(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "alertops_incidents":
        records.append(
          self._deliver_alertops(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "signl4_incidents":
        records.append(
          self._deliver_signl4(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "ilert_incidents":
        records.append(
          self._deliver_ilert(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "betterstack_incidents":
        records.append(
          self._deliver_betterstack(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "onpage_incidents":
        records.append(
          self._deliver_onpage(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "allquiet_incidents":
        records.append(
          self._deliver_allquiet(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "moogsoft_incidents":
        records.append(
          self._deliver_moogsoft(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "spikesh_incidents":
        records.append(
          self._deliver_spikesh(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "dutycalls_incidents":
        records.append(
          self._deliver_dutycalls(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "incidenthub_incidents":
        records.append(
          self._deliver_incidenthub(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "resolver_incidents":
        records.append(
          self._deliver_resolver(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "openduty_incidents":
        records.append(
          self._deliver_openduty(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "cabot_incidents":
        records.append(
          self._deliver_cabot(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "haloitsm_incidents":
        records.append(
          self._deliver_haloitsm(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "incidentmanagerio_incidents":
        records.append(
          self._deliver_incidentmanagerio(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "oneuptime_incidents":
        records.append(
          self._deliver_oneuptime(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "squzy_incidents":
        records.append(
          self._deliver_squzy(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "opsramp_incidents":
        records.append(
          self._deliver_opsramp(
            incident=incident,
            attempt_number=attempt_number,
            phase=phase,
          )
        )
        continue
      if target == "opsgenie_alerts":
        records.append(self._deliver_opsgenie(incident=incident, attempt_number=attempt_number, phase=phase))
    return tuple(records)

  def sync_incident_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None = None,
    attempt_number: int = 1,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    normalized_provider = provider.strip().lower().replace("-", "_")
    normalized_action = action.strip().lower().replace("-", "_")
    if normalized_provider == "pagerduty":
      return (
        self._sync_pagerduty_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "incidentio":
      return (
        self._sync_incidentio_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "firehydrant":
      return (
        self._sync_firehydrant_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "rootly":
      return (
        self._sync_rootly_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "blameless":
      return (
        self._sync_blameless_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "xmatters":
      return (
        self._sync_xmatters_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "servicenow":
      return (
        self._sync_servicenow_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "squadcast":
      return (
        self._sync_squadcast_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "bigpanda":
      return (
        self._sync_bigpanda_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "grafana_oncall":
      return (
        self._sync_grafana_oncall_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "zenduty":
      return (
        self._sync_zenduty_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "splunk_oncall":
      return (
        self._sync_splunk_oncall_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "jira_service_management":
      return (
        self._sync_jira_service_management_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "pagertree":
      return (
        self._sync_pagertree_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "alertops":
      return (
        self._sync_alertops_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "signl4":
      return (
        self._sync_signl4_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "ilert":
      return (
        self._sync_ilert_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "betterstack":
      return (
        self._sync_betterstack_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "onpage":
      return (
        self._sync_onpage_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "allquiet":
      return (
        self._sync_allquiet_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "moogsoft":
      return (
        self._sync_moogsoft_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "spikesh":
      return (
        self._sync_spikesh_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "dutycalls":
      return (
        self._sync_dutycalls_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "incidenthub":
      return (
        self._sync_incidenthub_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "resolver":
      return (
        self._sync_resolver_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "openduty":
      return (
        self._sync_openduty_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "cabot":
      return (
        self._sync_cabot_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "haloitsm":
      return (
        self._sync_haloitsm_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "incidentmanagerio":
      return (
        self._sync_incidentmanagerio_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "oneuptime":
      return (
        self._sync_oneuptime_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "squzy":
      return (
        self._sync_squzy_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "opsramp":
      return (
        self._sync_opsramp_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "opsgenie":
      return (
        self._sync_opsgenie_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    attempted_at = self._clock()
    return (
      OperatorIncidentDelivery(
        delivery_id=(
          f"{incident.event_id}:{normalized_provider}_workflow:{normalized_action}:attempt-{attempt_number}"
        ),
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=f"{normalized_provider}_workflow",
        status="failed",
        attempted_at=attempted_at,
        detail=f"provider_workflow_unsupported:{normalized_provider}:{normalized_action}",
        attempt_number=attempt_number,
        phase=f"provider_{normalized_action}",
        provider_action=normalized_action,
        external_provider=normalized_provider,
        external_reference=incident.provider_workflow_reference or incident.external_reference,
        source=incident.source,
      ),
    )

  def pull_incident_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
  ) -> OperatorIncidentProviderPullSync | None:
    normalized_provider = provider.strip().lower().replace("-", "_")
    if normalized_provider == "pagerduty":
      return self._pull_pagerduty_workflow_state(incident=incident)
    if normalized_provider == "incidentio":
      return self._pull_incidentio_workflow_state(incident=incident)
    if normalized_provider == "firehydrant":
      return self._pull_firehydrant_workflow_state(incident=incident)
    if normalized_provider == "rootly":
      return self._pull_rootly_workflow_state(incident=incident)
    if normalized_provider == "blameless":
      return self._pull_blameless_workflow_state(incident=incident)
    if normalized_provider == "xmatters":
      return self._pull_xmatters_workflow_state(incident=incident)
    if normalized_provider == "servicenow":
      return self._pull_servicenow_workflow_state(incident=incident)
    if normalized_provider == "squadcast":
      return self._pull_squadcast_workflow_state(incident=incident)
    if normalized_provider == "bigpanda":
      return self._pull_bigpanda_workflow_state(incident=incident)
    if normalized_provider == "grafana_oncall":
      return self._pull_grafana_oncall_workflow_state(incident=incident)
    if normalized_provider == "zenduty":
      return self._pull_zenduty_workflow_state(incident=incident)
    if normalized_provider == "splunk_oncall":
      return self._pull_splunk_oncall_workflow_state(incident=incident)
    if normalized_provider == "jira_service_management":
      return self._pull_jira_service_management_workflow_state(incident=incident)
    if normalized_provider == "pagertree":
      return self._pull_pagertree_workflow_state(incident=incident)
    if normalized_provider == "alertops":
      return self._pull_alertops_workflow_state(incident=incident)
    if normalized_provider == "signl4":
      return self._pull_signl4_workflow_state(incident=incident)
    if normalized_provider == "ilert":
      return self._pull_ilert_workflow_state(incident=incident)
    if normalized_provider == "betterstack":
      return self._pull_betterstack_workflow_state(incident=incident)
    if normalized_provider == "onpage":
      return self._pull_onpage_workflow_state(incident=incident)
    if normalized_provider == "allquiet":
      return self._pull_allquiet_workflow_state(incident=incident)
    if normalized_provider == "moogsoft":
      return self._pull_moogsoft_workflow_state(incident=incident)
    if normalized_provider == "spikesh":
      return self._pull_spikesh_workflow_state(incident=incident)
    if normalized_provider == "dutycalls":
      return self._pull_dutycalls_workflow_state(incident=incident)
    if normalized_provider == "incidenthub":
      return self._pull_incidenthub_workflow_state(incident=incident)
    if normalized_provider == "resolver":
      return self._pull_resolver_workflow_state(incident=incident)
    if normalized_provider == "openduty":
      return self._pull_openduty_workflow_state(incident=incident)
    if normalized_provider == "cabot":
      return self._pull_cabot_workflow_state(incident=incident)
    if normalized_provider == "haloitsm":
      return self._pull_haloitsm_workflow_state(incident=incident)
    if normalized_provider == "incidentmanagerio":
      return self._pull_incidentmanagerio_workflow_state(incident=incident)
    if normalized_provider == "oneuptime":
      return self._pull_oneuptime_workflow_state(incident=incident)
    if normalized_provider == "squzy":
      return self._pull_squzy_workflow_state(incident=incident)
    if normalized_provider == "opsramp":
      return self._pull_opsramp_workflow_state(incident=incident)
    if normalized_provider == "opsgenie":
      return self._pull_opsgenie_workflow_state(incident=incident)
    return None

  @staticmethod
  def _build_recovery_engine_template_context(
    *,
    workflow_reference: str | None,
    external_reference: str | None,
    job_id: str | None,
  ) -> dict[str, str]:
    context: dict[str, str] = {}
    for key, value in {
      "workflow_reference": workflow_reference,
      "reference": external_reference,
      "external_reference": external_reference,
      "job_id": job_id,
    }.items():
      if not value:
        continue
      context[key] = value
      context[f"{key}_urlencoded"] = urllib_parse.quote(value, safe="")
    return context

  @staticmethod
  def _format_recovery_engine_url(
    *,
    url_template: str | None,
    direct_url: str | None,
    workflow_reference: str | None,
    external_reference: str | None,
    job_id: str | None,
  ) -> str | None:
    if direct_url:
      return direct_url
    if not url_template:
      return None
    context = OperatorAlertDeliveryAdapter._build_recovery_engine_template_context(
      workflow_reference=workflow_reference,
      external_reference=external_reference,
      job_id=job_id,
    )
    try:
      return url_template.format_map(context)
    except KeyError:
      return None

  def _build_pagerduty_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    headers = {
      "Accept": "application/json",
    }
    if self._pagerduty_recovery_engine_token:
      headers["Authorization"] = f"Bearer {self._pagerduty_recovery_engine_token}"
    elif self._pagerduty_api_token:
      headers["Authorization"] = f"Token token={self._pagerduty_api_token}"
      headers["Accept"] = "application/vnd.pagerduty+json;version=2"
      if self._pagerduty_from_email:
        headers["From"] = self._pagerduty_from_email
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_opsgenie_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    api_key = self._opsgenie_recovery_engine_api_key or self._opsgenie_api_key
    headers = {
      "Accept": "application/json",
    }
    if api_key:
      headers["Authorization"] = f"GenieKey {api_key}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_incidentio_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._incidentio_recovery_engine_token or self._incidentio_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_firehydrant_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._firehydrant_recovery_engine_token or self._firehydrant_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_rootly_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._rootly_recovery_engine_token or self._rootly_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_blameless_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._blameless_recovery_engine_token or self._blameless_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_xmatters_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._xmatters_recovery_engine_token or self._xmatters_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_servicenow_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._servicenow_recovery_engine_token or self._servicenow_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_squadcast_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._squadcast_recovery_engine_token or self._squadcast_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_bigpanda_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._bigpanda_recovery_engine_token or self._bigpanda_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_grafana_oncall_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._grafana_oncall_recovery_engine_token or self._grafana_oncall_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_zenduty_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._zenduty_recovery_engine_token or self._zenduty_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_splunk_oncall_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._splunk_oncall_recovery_engine_token or self._splunk_oncall_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_jira_service_management_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = (
      self._jira_service_management_recovery_engine_token
      or self._jira_service_management_api_token
    )
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_pagertree_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._pagertree_recovery_engine_token or self._pagertree_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_alertops_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._alertops_recovery_engine_token or self._alertops_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_signl4_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._signl4_recovery_engine_token or self._signl4_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_ilert_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._ilert_recovery_engine_token or self._ilert_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_betterstack_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._betterstack_recovery_engine_token or self._betterstack_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_onpage_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._onpage_recovery_engine_token or self._onpage_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_allquiet_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._allquiet_recovery_engine_token or self._allquiet_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_moogsoft_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._moogsoft_recovery_engine_token or self._moogsoft_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_spikesh_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._spikesh_recovery_engine_token or self._spikesh_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_dutycalls_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._dutycalls_recovery_engine_token or self._dutycalls_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_incidenthub_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._incidenthub_recovery_engine_token or self._incidenthub_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_resolver_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._resolver_recovery_engine_token or self._resolver_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_openduty_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._openduty_recovery_engine_token or self._openduty_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_cabot_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._cabot_recovery_engine_token or self._cabot_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_haloitsm_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._haloitsm_recovery_engine_token or self._haloitsm_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_incidentmanagerio_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._incidentmanagerio_recovery_engine_token or self._incidentmanagerio_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_oneuptime_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._oneuptime_recovery_engine_token or self._oneuptime_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_squzy_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._squzy_recovery_engine_token or self._squzy_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_opsramp_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._opsramp_recovery_engine_token or self._opsramp_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _normalize_recovery_engine_payload(
    self,
    *,
    payload: dict[str, Any],
    provider: str,
  ) -> dict[str, Any]:
    body = self._extract_mapping(
      payload.get("data"),
      payload.get("job"),
      payload.get("telemetry"),
      payload,
    )
    telemetry = self._extract_mapping(
      body.get("telemetry"),
      body.get("status"),
      body.get("progress"),
    )
    merged = {**body, **telemetry}
    state = self._first_non_empty_string(
      merged.get("state"),
      merged.get("status"),
      merged.get("phase"),
    )
    progress = (
      merged.get("progress_percent")
      if isinstance(merged.get("progress_percent"), int)
      else (
        merged.get("progressPercent")
        if isinstance(merged.get("progressPercent"), int)
        else (
          merged.get("completion_percent")
          if isinstance(merged.get("completion_percent"), int)
          else merged.get("percent_complete")
        )
      )
    )
    attempt_count = (
      merged.get("attempt_count")
      if isinstance(merged.get("attempt_count"), int)
      else (
        merged.get("attempts")
        if isinstance(merged.get("attempts"), int)
        else merged.get("retry_count")
      )
    )
    return {
      "source": "provider_engine",
      "state": state,
      "progress_percent": progress,
      "attempt_count": attempt_count,
      "current_step": self._first_non_empty_string(
        merged.get("current_step"),
        merged.get("step"),
        merged.get("stage"),
        merged.get("phase"),
      ),
      "last_message": self._first_non_empty_string(
        merged.get("last_message"),
        merged.get("message"),
        merged.get("summary"),
        merged.get("detail"),
      ),
      "last_error": self._first_non_empty_string(
        merged.get("last_error"),
        merged.get("error"),
      ),
      "external_run_id": self._first_non_empty_string(
        merged.get("external_run_id"),
        merged.get("run_id"),
        merged.get("execution_id"),
        merged.get("job_id"),
        merged.get("id"),
      ),
      "job_url": self._first_non_empty_string(
        merged.get("job_url"),
        merged.get("url"),
        merged.get("html_url"),
      ),
      "started_at": self._parse_provider_datetime(
        merged.get("started_at"),
        merged.get("created_at"),
        merged.get("createdAt"),
      ),
      "finished_at": self._parse_provider_datetime(
        merged.get("finished_at"),
        merged.get("completed_at"),
        merged.get("completedAt"),
        merged.get("finishedAt"),
      ),
      "updated_at": self._parse_provider_datetime(
        merged.get("updated_at"),
        merged.get("updatedAt"),
        merged.get("last_update_at"),
        merged.get("lastUpdateAt"),
      ),
      "provider": provider,
    }

  def _poll_recovery_engine_payload(
    self,
    *,
    provider: str,
    workflow_reference: str | None,
    external_reference: str | None,
    direct_url: str | None,
    job_id: str | None,
  ) -> dict[str, Any]:
    if provider == "pagerduty":
      url = self._format_recovery_engine_url(
        url_template=self._pagerduty_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_pagerduty_recovery_engine_request(url=url)
    elif provider == "incidentio":
      url = self._format_recovery_engine_url(
        url_template=self._incidentio_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_incidentio_recovery_engine_request(url=url)
    elif provider == "firehydrant":
      url = self._format_recovery_engine_url(
        url_template=self._firehydrant_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_firehydrant_recovery_engine_request(url=url)
    elif provider == "rootly":
      url = self._format_recovery_engine_url(
        url_template=self._rootly_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_rootly_recovery_engine_request(url=url)
    elif provider == "blameless":
      url = self._format_recovery_engine_url(
        url_template=self._blameless_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_blameless_recovery_engine_request(url=url)
    elif provider == "xmatters":
      url = self._format_recovery_engine_url(
        url_template=self._xmatters_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_xmatters_recovery_engine_request(url=url)
    elif provider == "servicenow":
      url = self._format_recovery_engine_url(
        url_template=self._servicenow_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_servicenow_recovery_engine_request(url=url)
    elif provider == "squadcast":
      url = self._format_recovery_engine_url(
        url_template=self._squadcast_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_squadcast_recovery_engine_request(url=url)
    elif provider == "bigpanda":
      url = self._format_recovery_engine_url(
        url_template=self._bigpanda_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_bigpanda_recovery_engine_request(url=url)
    elif provider == "grafana_oncall":
      url = self._format_recovery_engine_url(
        url_template=self._grafana_oncall_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_grafana_oncall_recovery_engine_request(url=url)
    elif provider == "zenduty":
      url = self._format_recovery_engine_url(
        url_template=self._zenduty_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_zenduty_recovery_engine_request(url=url)
    elif provider == "splunk_oncall":
      url = self._format_recovery_engine_url(
        url_template=self._splunk_oncall_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_splunk_oncall_recovery_engine_request(url=url)
    elif provider == "jira_service_management":
      url = self._format_recovery_engine_url(
        url_template=self._jira_service_management_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_jira_service_management_recovery_engine_request(url=url)
    elif provider == "pagertree":
      url = self._format_recovery_engine_url(
        url_template=self._pagertree_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_pagertree_recovery_engine_request(url=url)
    elif provider == "alertops":
      url = self._format_recovery_engine_url(
        url_template=self._alertops_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_alertops_recovery_engine_request(url=url)
    elif provider == "signl4":
      url = self._format_recovery_engine_url(
        url_template=self._signl4_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_signl4_recovery_engine_request(url=url)
    elif provider == "ilert":
      url = self._format_recovery_engine_url(
        url_template=self._ilert_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_ilert_recovery_engine_request(url=url)
    elif provider == "betterstack":
      url = self._format_recovery_engine_url(
        url_template=self._betterstack_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_betterstack_recovery_engine_request(url=url)
    elif provider == "onpage":
      url = self._format_recovery_engine_url(
        url_template=self._onpage_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_onpage_recovery_engine_request(url=url)
    elif provider == "allquiet":
      url = self._format_recovery_engine_url(
        url_template=self._allquiet_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_allquiet_recovery_engine_request(url=url)
    elif provider == "moogsoft":
      url = self._format_recovery_engine_url(
        url_template=self._moogsoft_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_moogsoft_recovery_engine_request(url=url)
    elif provider == "spikesh":
      url = self._format_recovery_engine_url(
        url_template=self._spikesh_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_spikesh_recovery_engine_request(url=url)
    elif provider == "dutycalls":
      url = self._format_recovery_engine_url(
        url_template=self._dutycalls_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_dutycalls_recovery_engine_request(url=url)
    elif provider == "incidenthub":
      url = self._format_recovery_engine_url(
        url_template=self._incidenthub_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_incidenthub_recovery_engine_request(url=url)
    elif provider == "resolver":
      url = self._format_recovery_engine_url(
        url_template=self._resolver_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_resolver_recovery_engine_request(url=url)
    elif provider == "openduty":
      url = self._format_recovery_engine_url(
        url_template=self._openduty_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_openduty_recovery_engine_request(url=url)
    elif provider == "cabot":
      url = self._format_recovery_engine_url(
        url_template=self._cabot_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_cabot_recovery_engine_request(url=url)
    elif provider == "haloitsm":
      url = self._format_recovery_engine_url(
        url_template=self._haloitsm_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_haloitsm_recovery_engine_request(url=url)
    elif provider == "incidentmanagerio":
      url = self._format_recovery_engine_url(
        url_template=self._incidentmanagerio_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_incidentmanagerio_recovery_engine_request(url=url)
    elif provider == "oneuptime":
      url = self._format_recovery_engine_url(
        url_template=self._oneuptime_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_oneuptime_recovery_engine_request(url=url)
    elif provider == "squzy":
      url = self._format_recovery_engine_url(
        url_template=self._squzy_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_squzy_recovery_engine_request(url=url)
    elif provider == "opsramp":
      url = self._format_recovery_engine_url(
        url_template=self._opsramp_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_opsramp_recovery_engine_request(url=url)
    elif provider == "opsgenie":
      url = self._format_recovery_engine_url(
        url_template=self._opsgenie_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_opsgenie_recovery_engine_request(url=url)
    else:
      return {}
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return {}
    return self._normalize_recovery_engine_payload(payload=payload, provider=provider)

  def _deliver_console(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    LOGGER.warning(
      "operator-incident %s",
      json.dumps(
        {
          "event_id": incident.event_id,
          "alert_id": incident.alert_id,
          "kind": incident.kind,
          "severity": incident.severity,
          "summary": incident.summary,
          "detail": incident.detail,
          "run_id": incident.run_id,
          "session_id": incident.session_id,
          "source": incident.source,
          "delivery_targets": incident.delivery_targets,
        },
        default=str,
        sort_keys=True,
      ),
    )
    return OperatorIncidentDelivery(
      delivery_id=f"{incident.event_id}:operator_console:attempt-{attempt_number}",
      incident_event_id=incident.event_id,
      alert_id=incident.alert_id,
      incident_kind=incident.kind,
      target="operator_console",
      status="delivered",
      attempted_at=attempted_at,
      detail="logged_to_operator_console",
      attempt_number=attempt_number,
      phase=phase,
      source=incident.source,
    )

  def _deliver_webhook(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    if not self._webhook_url:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:operator_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="operator_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail="webhook_url_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )

    request = urllib_request.Request(
      self._webhook_url,
      data=self._build_generic_webhook_payload(incident=incident),
      headers={"Content-Type": "application/json"},
      method="POST",
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 200)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:operator_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="operator_webhook",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"webhook_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:operator_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="operator_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail=f"webhook_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )

  def _deliver_slack(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    if not self._slack_webhook_url:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:slack_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="slack_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail="slack_webhook_url_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )
    request = urllib_request.Request(
      self._slack_webhook_url,
      data=self._build_slack_payload(incident=incident),
      headers={"Content-Type": "application/json"},
      method="POST",
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 200)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:slack_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="slack_webhook",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"slack_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:slack_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="slack_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail=f"slack_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )

  def _deliver_pagerduty(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    if not self._pagerduty_integration_key:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagerduty_events:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagerduty_events",
        status="failed",
        attempted_at=attempted_at,
        detail="pagerduty_integration_key_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagerduty",
        external_reference=incident.external_reference or incident.alert_id,
        source=incident.source,
      )
    request = urllib_request.Request(
      "https://events.pagerduty.com/v2/enqueue",
      data=self._build_pagerduty_payload(incident=incident),
      headers={"Content-Type": "application/json"},
      method="POST",
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagerduty_events:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagerduty_events",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"pagerduty_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagerduty",
        external_reference=incident.external_reference or incident.alert_id,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagerduty_events:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagerduty_events",
        status="failed",
        attempted_at=attempted_at,
        detail=f"pagerduty_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagerduty",
        external_reference=incident.external_reference or incident.alert_id,
        source=incident.source,
      )

  def _sync_pagerduty_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    workflow_reference = incident.provider_workflow_reference or incident.external_reference
    target = "pagerduty_workflow"
    if not self._pagerduty_api_token or not self._pagerduty_from_email:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="pagerduty_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=workflow_reference,
        source=incident.source,
      )
    if not workflow_reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="pagerduty_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=None,
        source=incident.source,
      )

    request = self._build_pagerduty_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      workflow_reference=workflow_reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"pagerduty_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=workflow_reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"pagerduty_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=workflow_reference,
        source=incident.source,
      )

  def _deliver_incidentio(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._incidentio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="incidentio_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_incidentio_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentio_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidentio_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidentio_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_incidentio_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "incidentio_workflow"
    if not self._incidentio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidentio_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidentio_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_incidentio_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidentio_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidentio_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_incidentio_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidentio_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidentio_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(payload.get("incident"), payload.get("data"), payload)
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      incident_payload.get("custom_fields"),
      incident_payload.get("details"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": incident_payload.get("severity"),
      "mode": incident_payload.get("mode"),
      "visibility": incident_payload.get("visibility"),
      "url": incident_payload.get("url"),
      "updated_at": incident_payload.get("updated_at"),
      "assignee": self._first_non_empty_string(
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
        self._extract_mapping(incident_payload.get("assignee")).get("email"),
        incident_payload.get("assignee"),
      ),
    })
    return self._build_provider_pull_sync(
      provider="incidentio",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        incident_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("name"),
        incident_payload.get("summary"),
        incident_payload.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        incident_payload.get("updated_at"),
        incident_payload.get("created_at"),
      ),
    )

  def _deliver_firehydrant(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._firehydrant_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:firehydrant_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="firehydrant_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="firehydrant_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_firehydrant_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:firehydrant_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="firehydrant_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"firehydrant_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:firehydrant_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="firehydrant_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"firehydrant_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_firehydrant_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "firehydrant_workflow"
    if not self._firehydrant_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="firehydrant_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="firehydrant_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_firehydrant_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"firehydrant_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"firehydrant_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_firehydrant_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._firehydrant_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_firehydrant_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(payload.get("incident"), payload.get("data"), payload)
    details_payload = self._extract_mapping(
      incident_payload.get("details"),
      incident_payload.get("custom_fields"),
      incident_payload.get("metadata"),
    )
    provider_payload = dict(details_payload)
    provider_payload.update({
      "severity": incident_payload.get("severity"),
      "priority": incident_payload.get("priority"),
      "team": self._first_non_empty_string(
        self._extract_mapping(incident_payload.get("team")).get("name"),
        incident_payload.get("team"),
      ),
      "runbook": self._first_non_empty_string(
        self._extract_mapping(incident_payload.get("runbook")).get("name"),
        incident_payload.get("runbook"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        incident_payload.get("incident_url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": incident_payload.get("updated_at"),
      "external_reference": incident_payload.get("external_reference"),
    })
    return self._build_provider_pull_sync(
      provider="firehydrant",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        incident_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("name"),
        incident_payload.get("summary"),
        incident_payload.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        incident_payload.get("updated_at"),
        incident_payload.get("created_at"),
      ),
    )

  def _deliver_rootly(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._rootly_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:rootly_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="rootly_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="rootly_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_rootly_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:rootly_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="rootly_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"rootly_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:rootly_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="rootly_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"rootly_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_rootly_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "rootly_workflow"
    if not self._rootly_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="rootly_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="rootly_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_rootly_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"rootly_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"rootly_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_rootly_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._rootly_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_rootly_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      attributes.get("metadata"),
      attributes.get("details"),
      attributes.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity_id": self._first_non_empty_string(
        attributes.get("severity_id"),
        self._extract_mapping(attributes.get("severity")).get("id"),
      ),
      "private": attributes.get("private") if isinstance(attributes.get("private"), bool) else None,
      "slug": self._first_non_empty_string(
        attributes.get("slug"),
        attributes.get("short_id"),
      ),
      "url": self._first_non_empty_string(
        attributes.get("url"),
        attributes.get("html_url"),
      ),
      "acknowledged_at": attributes.get("acknowledged_at"),
      "updated_at": attributes.get("updated_at"),
      "external_reference": self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="rootly",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        attributes.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        attributes.get("title"),
        attributes.get("summary"),
        attributes.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        attributes.get("updated_at"),
        attributes.get("created_at"),
      ),
    )

  def _deliver_blameless(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._blameless_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:blameless_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="blameless_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="blameless_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="blameless",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_blameless_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:blameless_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="blameless_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"blameless_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="blameless",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:blameless_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="blameless_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"blameless_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="blameless",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_blameless_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "blameless_workflow"
    if not self._blameless_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="blameless_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="blameless",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="blameless_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="blameless",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_blameless_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"blameless_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="blameless",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"blameless_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="blameless",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_blameless_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._blameless_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_blameless_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      attributes.get("metadata"),
      attributes.get("details"),
      attributes.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": self._first_non_empty_string(
        attributes.get("severity"),
        self._extract_mapping(attributes.get("severity")).get("name"),
      ),
      "commander": self._first_non_empty_string(
        attributes.get("commander"),
        self._extract_mapping(attributes.get("commander")).get("name"),
        self._extract_mapping(attributes.get("owner")).get("name"),
      ),
      "visibility": self._first_non_empty_string(
        attributes.get("visibility"),
        attributes.get("visibility_mode"),
      ),
      "url": self._first_non_empty_string(
        attributes.get("url"),
        attributes.get("html_url"),
      ),
      "updated_at": attributes.get("updated_at"),
      "external_reference": self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="blameless",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        attributes.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        attributes.get("title"),
        attributes.get("summary"),
        attributes.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        attributes.get("updated_at"),
        attributes.get("created_at"),
      ),
    )

  def _deliver_xmatters(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._xmatters_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:xmatters_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="xmatters_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="xmatters_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="xmatters",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_xmatters_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:xmatters_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="xmatters_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"xmatters_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="xmatters",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:xmatters_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="xmatters_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"xmatters_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="xmatters",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_xmatters_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "xmatters_workflow"
    if not self._xmatters_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="xmatters_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="xmatters",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="xmatters_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="xmatters",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_xmatters_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"xmatters_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="xmatters",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"xmatters_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="xmatters",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_xmatters_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._xmatters_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_xmatters_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      attributes.get("metadata"),
      attributes.get("details"),
      attributes.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        attributes.get("priority"),
        self._extract_mapping(attributes.get("priority")).get("name"),
      ),
      "assignee": self._first_non_empty_string(
        attributes.get("assignee"),
        self._extract_mapping(attributes.get("assignee")).get("name"),
        self._extract_mapping(attributes.get("owner")).get("name"),
      ),
      "response_plan": self._first_non_empty_string(
        attributes.get("response_plan"),
        self._extract_mapping(attributes.get("response_plan")).get("name"),
      ),
      "url": self._first_non_empty_string(
        attributes.get("url"),
        attributes.get("html_url"),
      ),
      "updated_at": attributes.get("updated_at"),
      "external_reference": self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="xmatters",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        attributes.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        attributes.get("title"),
        attributes.get("summary"),
        attributes.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        attributes.get("updated_at"),
        attributes.get("created_at"),
      ),
    )

  def _deliver_servicenow(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._servicenow_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:servicenow_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="servicenow_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="servicenow_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="servicenow",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_servicenow_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:servicenow_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="servicenow_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"servicenow_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="servicenow",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:servicenow_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="servicenow_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"servicenow_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="servicenow",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_servicenow_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "servicenow_workflow"
    if not self._servicenow_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="servicenow_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicenow",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="servicenow_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicenow",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_servicenow_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"servicenow_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicenow",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"servicenow_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicenow",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_servicenow_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._servicenow_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_servicenow_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        incident_payload.get("priority"),
        attributes.get("priority"),
      ),
      "assigned_to": self._first_non_empty_string(
        incident_payload.get("assigned_to"),
        attributes.get("assigned_to"),
        self._extract_mapping(incident_payload.get("assigned_to")).get("name"),
      ),
      "assignment_group": self._first_non_empty_string(
        incident_payload.get("assignment_group"),
        attributes.get("assignment_group"),
        self._extract_mapping(incident_payload.get("assignment_group")).get("name"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="servicenow",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_number"),
        incident_payload.get("number"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("short_description"),
        incident_payload.get("summary"),
        attributes.get("short_description"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_squadcast(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._squadcast_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squadcast_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squadcast_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="squadcast_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_squadcast_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squadcast_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squadcast_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"squadcast_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squadcast_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squadcast_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"squadcast_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_squadcast_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "squadcast_workflow"
    if not self._squadcast_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="squadcast_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="squadcast_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_squadcast_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"squadcast_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"squadcast_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_squadcast_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._squadcast_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_squadcast_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": self._first_non_empty_string(
        incident_payload.get("severity"),
        incident_payload.get("priority"),
        attributes.get("severity"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "escalation_policy": self._first_non_empty_string(
        incident_payload.get("escalation_policy"),
        incident_payload.get("escalation_policy_name"),
        attributes.get("escalation_policy"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="squadcast",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("short_description"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_bigpanda(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._bigpanda_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:bigpanda_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="bigpanda_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="bigpanda_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="bigpanda",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_bigpanda_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:bigpanda_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="bigpanda_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"bigpanda_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="bigpanda",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:bigpanda_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="bigpanda_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"bigpanda_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="bigpanda",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_bigpanda_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "bigpanda_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._bigpanda_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="bigpanda_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bigpanda",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="bigpanda_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bigpanda",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_bigpanda_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"bigpanda_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bigpanda",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"bigpanda_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bigpanda",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_bigpanda_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._bigpanda_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_bigpanda_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": self._first_non_empty_string(
        incident_payload.get("severity"),
        incident_payload.get("priority"),
        attributes.get("severity"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "team": self._first_non_empty_string(
        incident_payload.get("team"),
        attributes.get("team"),
        self._extract_mapping(incident_payload.get("team")).get("name"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="bigpanda",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_grafana_oncall(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._grafana_oncall_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:grafana_oncall_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="grafana_oncall_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="grafana_oncall_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="grafana_oncall",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_grafana_oncall_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:grafana_oncall_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="grafana_oncall_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"grafana_oncall_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="grafana_oncall",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:grafana_oncall_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="grafana_oncall_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"grafana_oncall_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="grafana_oncall",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_grafana_oncall_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "grafana_oncall_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._grafana_oncall_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="grafana_oncall_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="grafana_oncall",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="grafana_oncall_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="grafana_oncall",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_grafana_oncall_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"grafana_oncall_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="grafana_oncall",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"grafana_oncall_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="grafana_oncall",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_grafana_oncall_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._grafana_oncall_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_grafana_oncall_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": self._first_non_empty_string(
        incident_payload.get("severity"),
        incident_payload.get("priority"),
        attributes.get("severity"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "escalation_chain": self._first_non_empty_string(
        incident_payload.get("escalation_chain"),
        incident_payload.get("escalation_chain_name"),
        attributes.get("escalation_chain"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="grafana_oncall",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_zenduty(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._zenduty_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zenduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zenduty_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="zenduty_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zenduty",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_zenduty_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zenduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zenduty_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"zenduty_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zenduty",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zenduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zenduty_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"zenduty_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zenduty",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_zenduty_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "zenduty_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._zenduty_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="zenduty_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zenduty",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="zenduty_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zenduty",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_zenduty_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"zenduty_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zenduty",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"zenduty_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zenduty",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_zenduty_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._zenduty_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_zenduty_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": self._first_non_empty_string(
        incident_payload.get("severity"),
        incident_payload.get("priority"),
        attributes.get("severity"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "service": self._first_non_empty_string(
        incident_payload.get("service"),
        incident_payload.get("service_name"),
        attributes.get("service"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="zenduty",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_splunk_oncall(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._splunk_oncall_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:splunk_oncall_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="splunk_oncall_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="splunk_oncall_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="splunk_oncall",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_splunk_oncall_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:splunk_oncall_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="splunk_oncall_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"splunk_oncall_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="splunk_oncall",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:splunk_oncall_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="splunk_oncall_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"splunk_oncall_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="splunk_oncall",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_splunk_oncall_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "splunk_oncall_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._splunk_oncall_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="splunk_oncall_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="splunk_oncall",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="splunk_oncall_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="splunk_oncall",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_splunk_oncall_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"splunk_oncall_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="splunk_oncall",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"splunk_oncall_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="splunk_oncall",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_splunk_oncall_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._splunk_oncall_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_splunk_oncall_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": self._first_non_empty_string(
        incident_payload.get("severity"),
        incident_payload.get("priority"),
        attributes.get("severity"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "routing_key": self._first_non_empty_string(
        incident_payload.get("routing_key"),
        incident_payload.get("routingKey"),
        attributes.get("routing_key"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="splunk_oncall",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_jira_service_management(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._jira_service_management_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:jira_service_management_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="jira_service_management_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="jira_service_management_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="jira_service_management",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_jira_service_management_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:jira_service_management_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="jira_service_management_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"jira_service_management_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="jira_service_management",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:jira_service_management_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="jira_service_management_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"jira_service_management_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="jira_service_management",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_jira_service_management_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "jira_service_management_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._jira_service_management_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="jira_service_management_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="jira_service_management",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="jira_service_management_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="jira_service_management",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_jira_service_management_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"jira_service_management_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="jira_service_management",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"jira_service_management_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="jira_service_management",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_jira_service_management_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._jira_service_management_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_jira_service_management_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        incident_payload.get("priority"),
        incident_payload.get("severity"),
        attributes.get("priority"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("display_name"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "service_project": self._first_non_empty_string(
        incident_payload.get("service_project"),
        incident_payload.get("project"),
        incident_payload.get("service_desk"),
        attributes.get("service_project"),
        attributes.get("project"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="jira_service_management",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_pagertree(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._pagertree_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagertree_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagertree_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="pagertree_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagertree",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_pagertree_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagertree_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagertree_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"pagertree_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagertree",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagertree_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagertree_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"pagertree_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagertree",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_pagertree_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "pagertree_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._pagertree_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="pagertree_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagertree",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="pagertree_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagertree",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_pagertree_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"pagertree_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagertree",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"pagertree_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagertree",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_pagertree_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._pagertree_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_pagertree_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "urgency": self._first_non_empty_string(
        incident_payload.get("urgency"),
        incident_payload.get("priority"),
        incident_payload.get("severity"),
        attributes.get("urgency"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("display_name"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "team": self._first_non_empty_string(
        incident_payload.get("team"),
        incident_payload.get("service"),
        attributes.get("team"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="pagertree",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_alertops(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._alertops_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:alertops_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="alertops_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="alertops_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="alertops",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_alertops_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:alertops_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="alertops_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"alertops_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="alertops",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:alertops_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="alertops_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"alertops_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="alertops",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_alertops_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "alertops_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._alertops_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="alertops_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="alertops",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="alertops_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="alertops",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_alertops_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"alertops_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="alertops",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"alertops_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="alertops",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_alertops_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._alertops_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_alertops_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        incident_payload.get("priority"),
        incident_payload.get("severity"),
        attributes.get("priority"),
      ),
      "owner": self._first_non_empty_string(
        incident_payload.get("owner"),
        incident_payload.get("assignee"),
        attributes.get("owner"),
        self._extract_mapping(incident_payload.get("owner")).get("display_name"),
        self._extract_mapping(incident_payload.get("owner")).get("name"),
      ),
      "service": self._first_non_empty_string(
        incident_payload.get("service"),
        incident_payload.get("team"),
        attributes.get("service"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="alertops",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_signl4(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._signl4_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:signl4_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="signl4_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="signl4_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="signl4",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_signl4_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:signl4_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="signl4_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"signl4_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="signl4",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:signl4_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="signl4_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"signl4_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="signl4",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_signl4_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "signl4_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._signl4_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="signl4_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="signl4",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="signl4_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="signl4",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_signl4_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"signl4_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="signl4",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"signl4_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="signl4",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_signl4_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._signl4_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_signl4_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "team": self._first_non_empty_string(
        alert_payload.get("team"),
        alert_payload.get("service"),
        attributes.get("team"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="signl4",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_ilert(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._ilert_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:ilert_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="ilert_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="ilert_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="ilert",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_ilert_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:ilert_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="ilert_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"ilert_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="ilert",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:ilert_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="ilert_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"ilert_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="ilert",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_ilert_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "ilert_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._ilert_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="ilert_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="ilert",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="ilert_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="ilert",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_ilert_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"ilert_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="ilert",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"ilert_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="ilert",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_ilert_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._ilert_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_ilert_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="ilert",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_betterstack(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._betterstack_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:betterstack_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="betterstack_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="betterstack_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="betterstack",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_betterstack_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:betterstack_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="betterstack_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"betterstack_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="betterstack",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:betterstack_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="betterstack_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"betterstack_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="betterstack",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_betterstack_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "betterstack_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._betterstack_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="betterstack_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="betterstack",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="betterstack_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="betterstack",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_betterstack_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"betterstack_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="betterstack",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"betterstack_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="betterstack",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_betterstack_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._betterstack_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_betterstack_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="betterstack",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_onpage(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._onpage_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:onpage_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="onpage_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="onpage_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_onpage_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:onpage_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="onpage_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"onpage_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:onpage_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="onpage_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"onpage_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_onpage_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "onpage_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._onpage_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="onpage_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="onpage_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_onpage_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"onpage_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"onpage_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_onpage_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._onpage_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_onpage_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="onpage",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_allquiet(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._allquiet_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:allquiet_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="allquiet_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="allquiet_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_allquiet_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:allquiet_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="allquiet_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"allquiet_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:allquiet_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="allquiet_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"allquiet_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_allquiet_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "allquiet_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._allquiet_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="allquiet_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="allquiet_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_allquiet_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"allquiet_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"allquiet_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_allquiet_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._allquiet_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_allquiet_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="allquiet",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_moogsoft(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._moogsoft_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:moogsoft_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="moogsoft_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="moogsoft_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_moogsoft_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:moogsoft_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="moogsoft_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"moogsoft_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:moogsoft_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="moogsoft_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"moogsoft_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_moogsoft_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "moogsoft_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._moogsoft_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="moogsoft_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="moogsoft_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_moogsoft_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"moogsoft_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"moogsoft_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_moogsoft_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._moogsoft_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_moogsoft_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="moogsoft",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_spikesh(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._spikesh_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:spikesh_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="spikesh_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="spikesh_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_spikesh_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:spikesh_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="spikesh_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"spikesh_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:spikesh_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="spikesh_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"spikesh_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_spikesh_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "spikesh_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._spikesh_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="spikesh_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="spikesh_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_spikesh_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"spikesh_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"spikesh_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_spikesh_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._spikesh_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_spikesh_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="spikesh",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_dutycalls(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._dutycalls_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:dutycalls_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="dutycalls_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="dutycalls_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_dutycalls_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:dutycalls_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="dutycalls_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"dutycalls_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:dutycalls_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="dutycalls_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"dutycalls_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_dutycalls_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "dutycalls_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._dutycalls_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="dutycalls_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="dutycalls_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_dutycalls_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"dutycalls_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"dutycalls_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_dutycalls_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._dutycalls_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_dutycalls_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="dutycalls",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_incidenthub(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._incidenthub_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidenthub_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidenthub_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="incidenthub_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_incidenthub_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidenthub_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidenthub_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidenthub_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidenthub_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidenthub_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidenthub_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_incidenthub_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "incidenthub_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidenthub_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidenthub_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidenthub_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidenthub_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidenthub_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidenthub_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_incidenthub_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidenthub_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidenthub_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="incidenthub",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_resolver(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._resolver_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:resolver_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="resolver_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="resolver_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_resolver_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:resolver_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="resolver_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"resolver_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:resolver_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="resolver_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"resolver_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_resolver_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "resolver_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._resolver_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="resolver_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="resolver_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_resolver_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"resolver_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"resolver_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_resolver_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._resolver_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_resolver_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="resolver",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_openduty(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._openduty_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:openduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="openduty_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="openduty_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_openduty_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:openduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="openduty_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"openduty_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:openduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="openduty_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"openduty_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_openduty_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "openduty_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._openduty_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="openduty_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="openduty_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_openduty_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"openduty_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"openduty_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_openduty_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._openduty_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_openduty_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="openduty",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_cabot(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._cabot_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:cabot_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="cabot_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="cabot_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_cabot_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:cabot_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="cabot_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"cabot_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:cabot_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="cabot_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"cabot_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_cabot_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "cabot_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._cabot_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="cabot_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="cabot_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_cabot_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"cabot_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"cabot_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_cabot_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._cabot_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_cabot_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="cabot",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_haloitsm(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._haloitsm_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:haloitsm_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="haloitsm_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="haloitsm_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_haloitsm_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:haloitsm_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="haloitsm_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"haloitsm_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:haloitsm_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="haloitsm_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"haloitsm_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_haloitsm_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "haloitsm_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._haloitsm_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="haloitsm_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="haloitsm_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_haloitsm_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"haloitsm_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"haloitsm_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_haloitsm_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._haloitsm_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_haloitsm_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="haloitsm",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_incidentmanagerio(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._incidentmanagerio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentmanagerio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentmanagerio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="incidentmanagerio_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_incidentmanagerio_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentmanagerio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentmanagerio_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidentmanagerio_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentmanagerio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentmanagerio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidentmanagerio_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_incidentmanagerio_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "incidentmanagerio_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidentmanagerio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidentmanagerio_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidentmanagerio_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidentmanagerio_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidentmanagerio_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidentmanagerio_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_incidentmanagerio_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidentmanagerio_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidentmanagerio_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="incidentmanagerio",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_oneuptime(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._oneuptime_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:oneuptime_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="oneuptime_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="oneuptime_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_oneuptime_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:oneuptime_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="oneuptime_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"oneuptime_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:oneuptime_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="oneuptime_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"oneuptime_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_squzy(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._squzy_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squzy_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squzy_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="squzy_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_squzy_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squzy_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squzy_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"squzy_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squzy_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squzy_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"squzy_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_oneuptime_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "oneuptime_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._oneuptime_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="oneuptime_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="oneuptime_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_oneuptime_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"oneuptime_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"oneuptime_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_squzy_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "squzy_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._squzy_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="squzy_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="squzy_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_squzy_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"squzy_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"squzy_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_oneuptime_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._oneuptime_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_oneuptime_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="oneuptime",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _pull_squzy_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._squzy_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_squzy_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="squzy",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_opsramp(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._opsramp_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsramp_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsramp_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="opsramp_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_opsramp_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsramp_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsramp_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"opsramp_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsramp_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsramp_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"opsramp_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_opsramp_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    target = "opsramp_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._opsramp_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="opsramp_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="opsramp_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_opsramp_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"opsramp_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"opsramp_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_opsramp_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._opsramp_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_opsramp_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="opsramp",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_opsgenie(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    alias = incident.external_reference or incident.alert_id
    if not self._opsgenie_api_key:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsgenie_alerts:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsgenie_alerts",
        status="failed",
        attempted_at=attempted_at,
        detail="opsgenie_api_key_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsgenie",
        external_reference=alias,
        source=incident.source,
      )
    request = self._build_opsgenie_delivery_request(incident=incident, alias=alias)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsgenie_alerts:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsgenie_alerts",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"opsgenie_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsgenie",
        external_reference=alias,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsgenie_alerts:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsgenie_alerts",
        status="failed",
        attempted_at=attempted_at,
        detail=f"opsgenie_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsgenie",
        external_reference=alias,
        source=incident.source,
      )

  def _sync_opsgenie_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "alias"
    target = "opsgenie_workflow"
    if not self._opsgenie_api_key:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="opsgenie_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="opsgenie_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_opsgenie_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"opsgenie_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"opsgenie_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_pagerduty_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    workflow_reference = incident.provider_workflow_reference or incident.external_reference
    if not self._pagerduty_api_token or not self._pagerduty_from_email or not workflow_reference:
      return None
    request = self._build_pagerduty_pull_request(workflow_reference=workflow_reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(payload.get("incident"), payload)
    body_payload = self._extract_mapping(
      incident_payload.get("body"),
      incident_payload.get("custom_details"),
      incident_payload.get("details"),
    )
    custom_details = self._extract_mapping(
      incident_payload.get("custom_details"),
      body_payload.get("details"),
      body_payload,
    )
    provider_payload = dict(custom_details)
    provider_payload.update({
      "urgency": incident_payload.get("urgency"),
      "html_url": incident_payload.get("html_url"),
      "last_status_change_at": incident_payload.get("last_status_change_at"),
      "service": self._extract_mapping(incident_payload.get("service")),
      "escalation_policy": self._extract_mapping(incident_payload.get("escalation_policy")),
    })
    return self._build_provider_pull_sync(
      provider="pagerduty",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        workflow_reference,
      ),
      external_reference=self._first_non_empty_string(
        incident_payload.get("incident_key"),
        incident.alert_id,
        workflow_reference,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("title"),
        incident_payload.get("summary"),
        incident_payload.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        incident_payload.get("last_status_change_at"),
        incident_payload.get("updated_at"),
        payload.get("updated_at"),
      ),
    )

  def _pull_opsgenie_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._opsgenie_api_key or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "alias"
    request = self._build_opsgenie_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(payload.get("data"), payload)
    details_payload = self._extract_mapping(
      alert_payload.get("details"),
      alert_payload.get("detail"),
    )
    provider_payload = dict(details_payload)
    provider_payload.update({
      "priority": alert_payload.get("priority"),
      "owner": self._extract_mapping(alert_payload.get("owner")),
      "acknowledged": alert_payload.get("acknowledged"),
      "seen": alert_payload.get("isSeen"),
      "tinyId": alert_payload.get("tinyId"),
      "teams": [
        team.get("name")
        for team in alert_payload.get("teams", [])
        if isinstance(team, dict) and isinstance(team.get("name"), str)
      ] if isinstance(alert_payload.get("teams"), list) else details_payload.get("teams"),
      "updatedAt": alert_payload.get("updatedAt"),
    })
    workflow_state = self._first_non_empty_string(alert_payload.get("status"))
    acknowledged = alert_payload.get("acknowledged")
    if workflow_state is None and isinstance(acknowledged, bool):
      workflow_state = "acknowledged" if acknowledged else "triggered"
    return self._build_provider_pull_sync(
      provider="opsgenie",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        alert_payload.get("alias"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=workflow_state or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("message"),
        alert_payload.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        alert_payload.get("updatedAt"),
        alert_payload.get("updated_at"),
        alert_payload.get("createdAt"),
      ),
    )

  @staticmethod
  def _resolve_pagerduty_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"triggered", "acknowledged", "resolved"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_responder_phase(incident_phase: str) -> str:
    if incident_phase == "triggered":
      return "awaiting_acknowledgment"
    if incident_phase == "acknowledged":
      return "engaged"
    if incident_phase == "resolved":
      return "resolved"
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_urgency_phase(urgency: str | None) -> str:
    normalized = (urgency or "").strip().lower().replace(" ", "_")
    if normalized == "high":
      return "high_urgency"
    if normalized == "low":
      return "low_urgency"
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state == "resolved":
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_opsgenie_alert_phase(status: str | None, acknowledged: bool | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "acknowledged", "closed"}:
      return normalized
    if acknowledged is True:
      return "acknowledged"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_acknowledgment_phase(alert_phase: str, acknowledged: bool | None) -> str:
    if alert_phase == "closed":
      return "closed"
    if acknowledged is True or alert_phase == "acknowledged":
      return "acknowledged"
    if alert_phase == "open":
      return "pending_acknowledgment"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_ownership_phase(owner: str | None, teams: list[str]) -> str:
    if owner:
      return "assigned"
    if teams:
      return "team_routed"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_visibility_phase(seen: bool | None) -> str:
    if seen is True:
      return "seen"
    if seen is False:
      return "unseen"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state == "closed":
      return "closed_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_close"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "recovery_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "alert_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_incidentio_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"active", "acknowledged", "resolved", "closed"}:
      return normalized
    if normalized in {"triaged"}:
      return "acknowledged"
    return "unknown"

  @staticmethod
  def _resolve_incidentio_assignment_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_incidentio_visibility_phase(visibility: str | None) -> str:
    normalized = (visibility or "").strip().lower().replace(" ", "_")
    if normalized in {"public", "private"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_incidentio_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"critical", "high", "warning", "medium", "low"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_incidentio_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"closed", "resolved"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_firehydrant_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "investigating", "mitigating", "monitoring", "resolved", "closed"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_ownership_phase(team: str | None) -> str:
    if team:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_firehydrant_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"sev1", "critical"}:
      return "critical"
    if normalized in {"sev2", "high"}:
      return "high"
    if normalized in {"sev3", "medium"}:
      return "medium"
    if normalized in {"sev4", "low"}:
      return "low"
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized in {"p1", "critical"}:
      return "critical"
    if normalized in {"p2", "high"}:
      return "high"
    if normalized in {"p3", "medium"}:
      return "medium"
    if normalized in {"p4", "low"}:
      return "low"
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"closed", "resolved"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_rootly_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_rootly_acknowledgment_phase(
    *,
    incident_phase: str,
    acknowledged_at: str | None,
  ) -> str:
    if incident_phase in {"resolved", "closed"}:
      return "closed"
    if acknowledged_at:
      return "acknowledged"
    if incident_phase == "acknowledged":
      return "acknowledged"
    if incident_phase in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "pending_acknowledgment"
    return "unknown"

  @staticmethod
  def _resolve_rootly_visibility_phase(private: bool | None) -> str:
    if private is True:
      return "private"
    if private is False:
      return "public"
    return "unknown"

  @staticmethod
  def _resolve_rootly_severity_phase(severity_id: str | None) -> str:
    normalized = (severity_id or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_rootly_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_blameless_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_blameless_command_phase(commander: str | None) -> str:
    return "assigned" if commander else "unassigned"

  @staticmethod
  def _resolve_blameless_visibility_phase(visibility: str | None) -> str:
    normalized = (visibility or "").strip().lower().replace(" ", "_")
    if normalized in {"public", "private", "internal"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_blameless_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_blameless_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_xmatters_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_xmatters_ownership_phase(assignee: str | None) -> str:
    return "assigned" if assignee else "unassigned"

  @staticmethod
  def _resolve_xmatters_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_xmatters_response_plan_phase(response_plan: str | None) -> str:
    return "configured" if response_plan else "unconfigured"

  @staticmethod
  def _resolve_xmatters_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_servicenow_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "new",
      "open",
      "acknowledged",
      "in_progress",
      "on_hold",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_servicenow_assignment_phase(
    *,
    assigned_to: str | None,
    assignment_group: str | None,
  ) -> str:
    if assigned_to:
      return "assigned_to_user"
    if assignment_group:
      return "assigned_to_group"
    return "unassigned"

  @staticmethod
  def _resolve_servicenow_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_servicenow_group_phase(assignment_group: str | None) -> str:
    return "group_configured" if assignment_group else "group_unconfigured"

  @staticmethod
  def _resolve_servicenow_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"new", "open", "in_progress", "on_hold"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_squadcast_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "on_hold",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_squadcast_ownership_phase(assignee: str | None) -> str:
    return "assigned" if assignee else "unassigned"

  @staticmethod
  def _resolve_squadcast_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_squadcast_escalation_phase(escalation_policy: str | None) -> str:
    return "configured" if escalation_policy else "unconfigured"

  @staticmethod
  def _resolve_squadcast_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "on_hold"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_bigpanda_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_bigpanda_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_bigpanda_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_bigpanda_team_phase(team: str | None) -> str:
    if team:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_bigpanda_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_grafana_oncall_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_grafana_oncall_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_grafana_oncall_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_grafana_oncall_escalation_phase(escalation_chain: str | None) -> str:
    if escalation_chain:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_grafana_oncall_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_zenduty_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_zenduty_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_zenduty_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_zenduty_service_phase(service: str | None) -> str:
    if service:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_zenduty_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_splunk_oncall_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_splunk_oncall_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_splunk_oncall_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_splunk_oncall_routing_phase(routing_key: str | None) -> str:
    if routing_key:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_splunk_oncall_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_jira_service_management_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_jira_service_management_assignment_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_jira_service_management_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_jira_service_management_project_phase(service_project: str | None) -> str:
    if service_project:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_jira_service_management_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_pagertree_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_pagertree_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_pagertree_urgency_phase(urgency: str | None) -> str:
    normalized = (urgency or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_pagertree_team_phase(team: str | None) -> str:
    if team:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_pagertree_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_alertops_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
      "escalated",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_alertops_ownership_phase(owner: str | None) -> str:
    if owner:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_alertops_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_alertops_service_phase(service: str | None) -> str:
    if service:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_alertops_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_signl4_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_signl4_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_signl4_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_signl4_team_phase(team: str | None) -> str:
    if team:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_signl4_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_ilert_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_ilert_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_ilert_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_ilert_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_ilert_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_betterstack_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_betterstack_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_betterstack_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_betterstack_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_betterstack_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_onpage_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_onpage_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_onpage_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_onpage_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_onpage_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_allquiet_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_allquiet_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_allquiet_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_allquiet_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_allquiet_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_moogsoft_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_moogsoft_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_moogsoft_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_moogsoft_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_moogsoft_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_provider_pull_sync(
    self,
    *,
    provider: str,
    workflow_reference: str | None,
    external_reference: str | None,
    workflow_state: str,
    detail: str | None,
    provider_payload: dict[str, Any],
    updated_at: datetime | None,
  ) -> OperatorIncidentProviderPullSync:
    remediation_payload = self._extract_mapping(
      provider_payload.get("remediation_provider_payload"),
      provider_payload.get("provider_payload"),
      provider_payload.get("remediation_payload"),
      provider_payload.get("payload"),
    )
    provider_recovery = self._extract_mapping(
      provider_payload.get("remediation_provider_recovery"),
      provider_payload.get("provider_recovery"),
      provider_payload.get("recovery"),
    )
    provider_telemetry = self._extract_mapping(
      provider_payload.get("remediation_provider_telemetry"),
      provider_payload.get("provider_telemetry"),
      provider_payload.get("telemetry"),
      provider_recovery.get("telemetry"),
    )
    provider_specific_recovery = self._extract_mapping(provider_recovery.get(provider))
    status_machine_payload = self._extract_mapping(
      provider_recovery.get("status_machine"),
      provider_payload.get("status_machine"),
    )
    job_id = self._first_non_empty_string(
      provider_recovery.get("job_id"),
      provider_payload.get("job_id"),
    )
    direct_telemetry_url = self._first_non_empty_string(
      provider_payload.get("remediation_provider_telemetry_url"),
      provider_payload.get("provider_telemetry_url"),
      provider_payload.get("telemetry_url"),
      self._extract_mapping(provider_recovery.get("telemetry")).get("job_url"),
    )
    engine_telemetry = self._poll_recovery_engine_payload(
      provider=provider,
      workflow_reference=workflow_reference,
      external_reference=external_reference,
      direct_url=direct_telemetry_url,
      job_id=job_id,
    )
    provider_schema_payload: dict[str, Any] = {}
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
      provider_schema_payload = {
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
    elif provider == "incidentio":
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
    elif provider == "bigpanda":
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
    elif provider == "signl4":
      signl4_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      signl4_team = self._first_non_empty_string(
        provider_specific_recovery.get("team"),
        provider_payload.get("team"),
        provider_payload.get("service"),
      )
      signl4_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      signl4_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      signl4_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_signl4_alert_phase(signl4_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "signl4",
        "signl4": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": signl4_status,
          "priority": signl4_priority,
          "team": signl4_team,
          "assignee": signl4_assignee,
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
            "alert_phase": signl4_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_signl4_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=signl4_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_signl4_ownership_phase(signl4_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_signl4_priority_phase(signl4_priority),
            "team_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("team_phase"),
            ) or self._resolve_signl4_team_phase(signl4_team),
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
          signl4_status,
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
    elif provider == "ilert":
      ilert_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      ilert_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      ilert_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      ilert_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      ilert_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_ilert_alert_phase(ilert_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "ilert",
        "ilert": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": ilert_status,
          "priority": ilert_priority,
          "escalation_policy": ilert_escalation_policy,
          "assignee": ilert_assignee,
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
            "alert_phase": ilert_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_ilert_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=ilert_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_ilert_ownership_phase(ilert_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_ilert_priority_phase(ilert_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_ilert_escalation_phase(ilert_escalation_policy),
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
          ilert_status,
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
    elif provider == "betterstack":
      betterstack_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      betterstack_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      betterstack_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      betterstack_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      betterstack_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_betterstack_alert_phase(betterstack_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "betterstack",
        "betterstack": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": betterstack_status,
          "priority": betterstack_priority,
          "escalation_policy": betterstack_escalation_policy,
          "assignee": betterstack_assignee,
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
            "alert_phase": betterstack_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_betterstack_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=betterstack_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_betterstack_ownership_phase(betterstack_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_betterstack_priority_phase(betterstack_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_betterstack_escalation_phase(betterstack_escalation_policy),
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
          betterstack_status,
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
    elif provider == "onpage":
      onpage_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      onpage_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      onpage_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      onpage_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      onpage_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_onpage_alert_phase(onpage_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "onpage",
        "onpage": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": onpage_status,
          "priority": onpage_priority,
          "escalation_policy": onpage_escalation_policy,
          "assignee": onpage_assignee,
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
            "alert_phase": onpage_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_onpage_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=onpage_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_onpage_ownership_phase(onpage_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_onpage_priority_phase(onpage_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_onpage_escalation_phase(onpage_escalation_policy),
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
          onpage_status,
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
    elif provider == "allquiet":
      allquiet_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      allquiet_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      allquiet_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      allquiet_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      allquiet_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_allquiet_alert_phase(allquiet_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "allquiet",
        "allquiet": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": allquiet_status,
          "priority": allquiet_priority,
          "escalation_policy": allquiet_escalation_policy,
          "assignee": allquiet_assignee,
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
            "alert_phase": allquiet_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_allquiet_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=allquiet_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_allquiet_ownership_phase(allquiet_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_allquiet_priority_phase(allquiet_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_allquiet_escalation_phase(allquiet_escalation_policy),
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
          allquiet_status,
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
    elif provider == "moogsoft":
      moogsoft_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      moogsoft_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      moogsoft_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      moogsoft_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      moogsoft_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(moogsoft_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "moogsoft",
        "moogsoft": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": moogsoft_status,
          "priority": moogsoft_priority,
          "escalation_policy": moogsoft_escalation_policy,
          "assignee": moogsoft_assignee,
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
            "alert_phase": moogsoft_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=moogsoft_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(moogsoft_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(moogsoft_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(moogsoft_escalation_policy),
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
          moogsoft_status,
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
    elif provider == "spikesh":
      spikesh_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      spikesh_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      spikesh_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      spikesh_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      spikesh_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(spikesh_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "spikesh",
        "spikesh": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": spikesh_status,
          "priority": spikesh_priority,
          "escalation_policy": spikesh_escalation_policy,
          "assignee": spikesh_assignee,
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
            "alert_phase": spikesh_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=spikesh_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(spikesh_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(spikesh_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(spikesh_escalation_policy),
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
          spikesh_status,
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
    elif provider == "dutycalls":
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
    elif provider == "oneuptime":
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
      provider_schema_payload = {
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
      provider_schema_payload = {
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
    elif provider == "opsramp":
      opsramp_priority = self._first_non_empty_string(
        provider_specific_recovery.get("priority"),
        provider_payload.get("priority"),
        provider_payload.get("severity"),
        provider_payload.get("urgency"),
      )
      opsramp_escalation_policy = self._first_non_empty_string(
        provider_specific_recovery.get("escalation_policy"),
        provider_payload.get("escalation_policy"),
        provider_payload.get("escalationPolicy"),
        provider_payload.get("policy"),
        provider_payload.get("source"),
      )
      opsramp_assignee = self._first_non_empty_string(
        provider_specific_recovery.get("assignee"),
        provider_payload.get("assignee"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner")).get("display_name"),
      )
      opsramp_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("alert_status"),
        provider_payload.get("status"),
        provider_payload.get("state"),
      ) or "unknown"
      opsramp_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_moogsoft_alert_phase(opsramp_status),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "opsramp",
        "opsramp": {
          "alert_id": self._first_non_empty_string(
            provider_specific_recovery.get("alert_id"),
            provider_payload.get("alert_id"),
            provider_payload.get("alertId"),
            provider_payload.get("id"),
            workflow_reference,
          ),
          "external_reference": external_reference,
          "alert_status": opsramp_status,
          "priority": opsramp_priority,
          "escalation_policy": opsramp_escalation_policy,
          "assignee": opsramp_assignee,
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
            "alert_phase": opsramp_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_moogsoft_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=opsramp_status,
            ),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_moogsoft_ownership_phase(opsramp_assignee),
            "priority_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("priority_phase"),
            ) or self._resolve_moogsoft_priority_phase(opsramp_priority),
            "escalation_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("escalation_phase"),
            ) or self._resolve_moogsoft_escalation_phase(opsramp_escalation_policy),
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
          opsramp_status,
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
    elif provider == "opsgenie":
      opsgenie_owner = self._first_non_empty_string(
        provider_specific_recovery.get("owner"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner_user")).get("username"),
      )
      opsgenie_acknowledged = (
        provider_specific_recovery.get("acknowledged")
        if isinstance(provider_specific_recovery.get("acknowledged"), bool)
        else (
          provider_payload.get("acknowledged")
          if isinstance(provider_payload.get("acknowledged"), bool)
          else None
        )
      )
      opsgenie_seen = (
        provider_specific_recovery.get("seen")
        if isinstance(provider_specific_recovery.get("seen"), bool)
        else (
          provider_payload.get("seen")
          if isinstance(provider_payload.get("seen"), bool)
          else None
        )
      )
      opsgenie_teams = self._extract_string_list(
        provider_specific_recovery.get("teams"),
        provider_payload.get("teams"),
        provider_payload.get("team"),
      )
      opsgenie_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_opsgenie_alert_phase(workflow_state, opsgenie_acknowledged),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "opsgenie",
        "opsgenie": {
          "alert_id": workflow_reference,
          "alias": external_reference,
          "alert_status": workflow_state,
          "priority": self._first_non_empty_string(provider_payload.get("priority")),
          "owner": self._first_non_empty_string(
            provider_payload.get("owner"),
            self._extract_mapping(provider_payload.get("owner_user")).get("username"),
          ),
          "acknowledged": (
            provider_payload.get("acknowledged")
            if isinstance(provider_payload.get("acknowledged"), bool)
            else None
          ),
          "seen": (
            provider_payload.get("seen")
            if isinstance(provider_payload.get("seen"), bool)
            else None
          ),
          "tiny_id": self._first_non_empty_string(
            provider_payload.get("tiny_id"),
            provider_payload.get("tinyId"),
          ),
          "teams": self._extract_string_list(
            provider_payload.get("teams"),
            provider_payload.get("team"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              provider_payload.get("updatedAt"),
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              provider_payload.get("updatedAt"),
            ) is not None
            else None
          ),
          "phase_graph": {
            "alert_phase": opsgenie_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_opsgenie_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=workflow_state,
            ),
            "acknowledgment_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("acknowledgment_phase"),
            ) or self._resolve_opsgenie_acknowledgment_phase(opsgenie_alert_phase, opsgenie_acknowledged),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_opsgenie_ownership_phase(opsgenie_owner, opsgenie_teams),
            "visibility_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("visibility_phase"),
            ) or self._resolve_opsgenie_visibility_phase(opsgenie_seen),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                provider_payload.get("updatedAt"),
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                provider_payload.get("updatedAt"),
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
        "updated_at": self._first_non_empty_string(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          provider_payload.get("updatedAt"),
        ),
      }
    merged_telemetry = {
      **provider_telemetry,
      **{key: value for key, value in engine_telemetry.items() if value is not None},
    }
    merged_payload: dict[str, Any] = dict(remediation_payload)
    merged_payload.update({
      "workflow_reference": workflow_reference,
      "workflow_state": workflow_state,
      "status": self._first_non_empty_string(
        provider_recovery.get("job_state"),
        provider_payload.get("remediation_state"),
        merged_telemetry.get("state"),
      ),
      "recovery_state": self._first_non_empty_string(
        provider_recovery.get("lifecycle_state"),
        provider_payload.get("recovery_state"),
      ),
      "job_id": self._first_non_empty_string(
        provider_recovery.get("job_id"),
        provider_payload.get("job_id"),
      ),
      "summary": self._first_non_empty_string(
        provider_payload.get("remediation_summary"),
        provider_recovery.get("summary"),
      ),
      "detail": self._first_non_empty_string(
        provider_payload.get("remediation_detail"),
        provider_recovery.get("detail"),
        detail,
      ),
      "channels": self._extract_string_list(
        provider_recovery.get("channels"),
        provider_payload.get("channels"),
      ),
      "targets": {
        "symbols": self._extract_string_list(
          provider_recovery.get("symbols"),
          provider_payload.get("symbols"),
        ),
        "timeframe": self._first_non_empty_string(
          provider_recovery.get("timeframe"),
          provider_payload.get("timeframe"),
        ),
      },
      "verification": {
        "state": self._first_non_empty_string(
          provider_recovery.get("verification_state"),
          self._extract_mapping(provider_recovery.get("verification")).get("state"),
          self._extract_mapping(provider_payload.get("verification")).get("state"),
        ),
      },
      "telemetry": {
        "source": self._first_non_empty_string(
          merged_telemetry.get("source"),
        ),
        "state": self._first_non_empty_string(
          merged_telemetry.get("state"),
          provider_recovery.get("job_state"),
          provider_payload.get("remediation_state"),
        ),
        "progress_percent": (
          merged_telemetry.get("progress_percent")
          if isinstance(merged_telemetry.get("progress_percent"), int)
          else merged_telemetry.get("progressPercent")
        ),
        "attempt_count": (
          merged_telemetry.get("attempt_count")
          if isinstance(merged_telemetry.get("attempt_count"), int)
          else (
            merged_telemetry.get("attempts")
            if isinstance(merged_telemetry.get("attempts"), int)
            else status_machine_payload.get("attempt_number")
          )
        ),
        "current_step": self._first_non_empty_string(
          merged_telemetry.get("current_step"),
          merged_telemetry.get("step"),
          merged_telemetry.get("phase"),
        ),
        "last_message": self._first_non_empty_string(
          merged_telemetry.get("last_message"),
          merged_telemetry.get("message"),
          merged_telemetry.get("summary"),
          provider_recovery.get("detail"),
          detail,
        ),
        "last_error": self._first_non_empty_string(
          merged_telemetry.get("last_error"),
          merged_telemetry.get("error"),
        ),
        "external_run_id": self._first_non_empty_string(
          merged_telemetry.get("external_run_id"),
          merged_telemetry.get("run_id"),
          merged_telemetry.get("execution_id"),
          provider_recovery.get("job_id"),
          provider_payload.get("job_id"),
        ),
        "job_url": self._first_non_empty_string(
          merged_telemetry.get("job_url"),
          merged_telemetry.get("url"),
        ),
        "started_at": self._parse_provider_datetime(
          merged_telemetry.get("started_at"),
          merged_telemetry.get("created_at"),
        ),
        "finished_at": self._parse_provider_datetime(
          merged_telemetry.get("finished_at"),
          merged_telemetry.get("completed_at"),
        ),
        "updated_at": self._parse_provider_datetime(
          merged_telemetry.get("updated_at"),
          merged_telemetry.get("last_update_at"),
          updated_at,
        ),
      },
      "status_machine": {
        "state": self._first_non_empty_string(
          provider_recovery.get("status_machine_state"),
          status_machine_payload.get("state"),
        ),
        "workflow_state": self._first_non_empty_string(
          provider_recovery.get("status_machine_workflow_state"),
          status_machine_payload.get("workflow_state"),
          workflow_state,
        ),
        "workflow_action": self._first_non_empty_string(
          provider_recovery.get("status_machine_workflow_action"),
          status_machine_payload.get("workflow_action"),
        ),
        "job_state": self._first_non_empty_string(
          provider_recovery.get("status_machine_job_state"),
          status_machine_payload.get("job_state"),
          provider_recovery.get("job_state"),
        ),
        "sync_state": (
          self._first_non_empty_string(
            provider_recovery.get("status_machine_sync_state"),
            status_machine_payload.get("sync_state"),
          )
          or "provider_authoritative"
        ),
        "last_event_kind": self._first_non_empty_string(
          status_machine_payload.get("last_event_kind"),
        ),
        "last_event_at": (
          self._parse_provider_datetime(status_machine_payload.get("last_event_at")) or updated_at
        ),
        "last_detail": self._first_non_empty_string(
          provider_recovery.get("detail"),
          status_machine_payload.get("last_detail"),
          detail,
        ),
        "attempt_number": (
          int(status_machine_payload.get("attempt_number"))
          if isinstance(status_machine_payload.get("attempt_number"), int)
          else 0
        ),
      },
      "provider_schema": provider_schema_payload,
    })
    remediation_state = self._first_non_empty_string(
      provider_payload.get("remediation_state"),
      provider_recovery.get("lifecycle_state"),
      provider_recovery.get("job_state"),
      merged_payload.get("status"),
    )
    return OperatorIncidentProviderPullSync(
      provider=provider,
      workflow_reference=workflow_reference,
      external_reference=external_reference,
      workflow_state=workflow_state,
      remediation_state=remediation_state,
      detail=detail,
      payload=merged_payload,
      synced_at=updated_at or self._clock(),
    )

  @staticmethod
  def _build_provider_recovery_payload(incident: OperatorIncidentEvent) -> dict[str, Any]:
    provider_recovery = incident.remediation.provider_recovery
    return {
      "lifecycle_state": provider_recovery.lifecycle_state,
      "provider": provider_recovery.provider,
      "job_id": provider_recovery.job_id,
      "reference": provider_recovery.reference,
      "workflow_reference": provider_recovery.workflow_reference,
      "summary": provider_recovery.summary,
      "detail": provider_recovery.detail,
      "channels": provider_recovery.channels,
      "symbols": provider_recovery.symbols,
      "timeframe": provider_recovery.timeframe,
      "updated_at": (
        provider_recovery.updated_at.isoformat()
        if provider_recovery.updated_at is not None
        else None
      ),
      "verification": {
        "state": provider_recovery.verification.state,
        "checked_at": (
          provider_recovery.verification.checked_at.isoformat()
          if provider_recovery.verification.checked_at is not None
          else None
        ),
        "summary": provider_recovery.verification.summary,
        "issues": provider_recovery.verification.issues,
      },
      "telemetry": {
        "source": provider_recovery.telemetry.source,
        "state": provider_recovery.telemetry.state,
        "progress_percent": provider_recovery.telemetry.progress_percent,
        "attempt_count": provider_recovery.telemetry.attempt_count,
        "current_step": provider_recovery.telemetry.current_step,
        "last_message": provider_recovery.telemetry.last_message,
        "last_error": provider_recovery.telemetry.last_error,
        "external_run_id": provider_recovery.telemetry.external_run_id,
        "job_url": provider_recovery.telemetry.job_url,
        "started_at": (
          provider_recovery.telemetry.started_at.isoformat()
          if provider_recovery.telemetry.started_at is not None
          else None
        ),
        "finished_at": (
          provider_recovery.telemetry.finished_at.isoformat()
          if provider_recovery.telemetry.finished_at is not None
          else None
        ),
        "updated_at": (
          provider_recovery.telemetry.updated_at.isoformat()
          if provider_recovery.telemetry.updated_at is not None
          else None
        ),
      },
      "status_machine": {
        "state": provider_recovery.status_machine.state,
        "workflow_state": provider_recovery.status_machine.workflow_state,
        "workflow_action": provider_recovery.status_machine.workflow_action,
        "job_state": provider_recovery.status_machine.job_state,
        "sync_state": provider_recovery.status_machine.sync_state,
        "last_event_kind": provider_recovery.status_machine.last_event_kind,
        "last_event_at": (
          provider_recovery.status_machine.last_event_at.isoformat()
          if provider_recovery.status_machine.last_event_at is not None
          else None
        ),
        "last_detail": provider_recovery.status_machine.last_detail,
        "attempt_number": provider_recovery.status_machine.attempt_number,
      },
      "provider_schema_kind": provider_recovery.provider_schema_kind,
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
      "dutycalls": {
        "alert_id": provider_recovery.dutycalls.alert_id,
        "external_reference": provider_recovery.dutycalls.external_reference,
        "alert_status": provider_recovery.dutycalls.alert_status,
        "priority": provider_recovery.dutycalls.priority,
        "escalation_policy": provider_recovery.dutycalls.escalation_policy,
        "assignee": provider_recovery.dutycalls.assignee,
        "url": provider_recovery.dutycalls.url,
        "updated_at": (
          provider_recovery.dutycalls.updated_at.isoformat()
          if provider_recovery.dutycalls.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.dutycalls.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.dutycalls.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.dutycalls.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.dutycalls.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.dutycalls.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.dutycalls.phase_graph.last_transition_at.isoformat()
            if provider_recovery.dutycalls.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "incidenthub": {
        "alert_id": provider_recovery.incidenthub.alert_id,
        "external_reference": provider_recovery.incidenthub.external_reference,
        "alert_status": provider_recovery.incidenthub.alert_status,
        "priority": provider_recovery.incidenthub.priority,
        "escalation_policy": provider_recovery.incidenthub.escalation_policy,
        "assignee": provider_recovery.incidenthub.assignee,
        "url": provider_recovery.incidenthub.url,
        "updated_at": (
          provider_recovery.incidenthub.updated_at.isoformat()
          if provider_recovery.incidenthub.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.incidenthub.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.incidenthub.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.incidenthub.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.incidenthub.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.incidenthub.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.incidenthub.phase_graph.last_transition_at.isoformat()
            if provider_recovery.incidenthub.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "resolver": {
        "alert_id": provider_recovery.resolver.alert_id,
        "external_reference": provider_recovery.resolver.external_reference,
        "alert_status": provider_recovery.resolver.alert_status,
        "priority": provider_recovery.resolver.priority,
        "escalation_policy": provider_recovery.resolver.escalation_policy,
        "assignee": provider_recovery.resolver.assignee,
        "url": provider_recovery.resolver.url,
        "updated_at": (
          provider_recovery.resolver.updated_at.isoformat()
          if provider_recovery.resolver.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.resolver.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.resolver.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.resolver.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.resolver.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.resolver.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.resolver.phase_graph.last_transition_at.isoformat()
            if provider_recovery.resolver.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "openduty": {
        "alert_id": provider_recovery.openduty.alert_id,
        "external_reference": provider_recovery.openduty.external_reference,
        "alert_status": provider_recovery.openduty.alert_status,
        "priority": provider_recovery.openduty.priority,
        "escalation_policy": provider_recovery.openduty.escalation_policy,
        "assignee": provider_recovery.openduty.assignee,
        "url": provider_recovery.openduty.url,
        "updated_at": (
          provider_recovery.openduty.updated_at.isoformat()
          if provider_recovery.openduty.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.openduty.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.openduty.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.openduty.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.openduty.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.openduty.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.openduty.phase_graph.last_transition_at.isoformat()
            if provider_recovery.openduty.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "cabot": {
        "alert_id": provider_recovery.cabot.alert_id,
        "external_reference": provider_recovery.cabot.external_reference,
        "alert_status": provider_recovery.cabot.alert_status,
        "priority": provider_recovery.cabot.priority,
        "escalation_policy": provider_recovery.cabot.escalation_policy,
        "assignee": provider_recovery.cabot.assignee,
        "url": provider_recovery.cabot.url,
        "updated_at": (
          provider_recovery.cabot.updated_at.isoformat()
          if provider_recovery.cabot.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.cabot.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.cabot.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.cabot.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.cabot.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.cabot.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.cabot.phase_graph.last_transition_at.isoformat()
            if provider_recovery.cabot.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "haloitsm": {
        "alert_id": provider_recovery.haloitsm.alert_id,
        "external_reference": provider_recovery.haloitsm.external_reference,
        "alert_status": provider_recovery.haloitsm.alert_status,
        "priority": provider_recovery.haloitsm.priority,
        "escalation_policy": provider_recovery.haloitsm.escalation_policy,
        "assignee": provider_recovery.haloitsm.assignee,
        "url": provider_recovery.haloitsm.url,
        "updated_at": (
          provider_recovery.haloitsm.updated_at.isoformat()
          if provider_recovery.haloitsm.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.haloitsm.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.haloitsm.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.haloitsm.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.haloitsm.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.haloitsm.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.haloitsm.phase_graph.last_transition_at.isoformat()
            if provider_recovery.haloitsm.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "incidentmanagerio": {
        "alert_id": provider_recovery.incidentmanagerio.alert_id,
        "external_reference": provider_recovery.incidentmanagerio.external_reference,
        "alert_status": provider_recovery.incidentmanagerio.alert_status,
        "priority": provider_recovery.incidentmanagerio.priority,
        "escalation_policy": provider_recovery.incidentmanagerio.escalation_policy,
        "assignee": provider_recovery.incidentmanagerio.assignee,
        "url": provider_recovery.incidentmanagerio.url,
        "updated_at": (
          provider_recovery.incidentmanagerio.updated_at.isoformat()
          if provider_recovery.incidentmanagerio.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.incidentmanagerio.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.incidentmanagerio.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.incidentmanagerio.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.incidentmanagerio.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.incidentmanagerio.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.incidentmanagerio.phase_graph.last_transition_at.isoformat()
            if provider_recovery.incidentmanagerio.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "oneuptime": {
        "alert_id": provider_recovery.oneuptime.alert_id,
        "external_reference": provider_recovery.oneuptime.external_reference,
        "alert_status": provider_recovery.oneuptime.alert_status,
        "priority": provider_recovery.oneuptime.priority,
        "escalation_policy": provider_recovery.oneuptime.escalation_policy,
        "assignee": provider_recovery.oneuptime.assignee,
        "url": provider_recovery.oneuptime.url,
        "updated_at": (
          provider_recovery.oneuptime.updated_at.isoformat()
          if provider_recovery.oneuptime.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.oneuptime.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.oneuptime.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.oneuptime.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.oneuptime.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.oneuptime.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.oneuptime.phase_graph.last_transition_at.isoformat()
            if provider_recovery.oneuptime.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "squzy": {
        "alert_id": provider_recovery.squzy.alert_id,
        "external_reference": provider_recovery.squzy.external_reference,
        "alert_status": provider_recovery.squzy.alert_status,
        "priority": provider_recovery.squzy.priority,
        "escalation_policy": provider_recovery.squzy.escalation_policy,
        "assignee": provider_recovery.squzy.assignee,
        "url": provider_recovery.squzy.url,
        "updated_at": (
          provider_recovery.squzy.updated_at.isoformat()
          if provider_recovery.squzy.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.squzy.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.squzy.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.squzy.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.squzy.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.squzy.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.squzy.phase_graph.last_transition_at.isoformat()
            if provider_recovery.squzy.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "opsramp": {
        "alert_id": provider_recovery.opsramp.alert_id,
        "external_reference": provider_recovery.opsramp.external_reference,
        "alert_status": provider_recovery.opsramp.alert_status,
        "priority": provider_recovery.opsramp.priority,
        "escalation_policy": provider_recovery.opsramp.escalation_policy,
        "assignee": provider_recovery.opsramp.assignee,
        "url": provider_recovery.opsramp.url,
        "updated_at": (
          provider_recovery.opsramp.updated_at.isoformat()
          if provider_recovery.opsramp.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.opsramp.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.opsramp.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.opsramp.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.opsramp.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.opsramp.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.opsramp.phase_graph.last_transition_at.isoformat()
            if provider_recovery.opsramp.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
    }

  @staticmethod
  def _build_generic_webhook_payload(*, incident: OperatorIncidentEvent) -> bytes:
    return json.dumps(
      {
        "event_id": incident.event_id,
        "alert_id": incident.alert_id,
        "kind": incident.kind,
        "timestamp": incident.timestamp.isoformat(),
        "severity": incident.severity,
        "summary": incident.summary,
        "detail": incident.detail,
        "run_id": incident.run_id,
        "session_id": incident.session_id,
        "source": incident.source,
        "remediation": {
          "state": incident.remediation.state,
          "kind": incident.remediation.kind,
          "owner": incident.remediation.owner,
          "summary": incident.remediation.summary,
          "detail": incident.remediation.detail,
          "runbook": incident.remediation.runbook,
          "provider": incident.remediation.provider,
          "reference": incident.remediation.reference,
          "provider_payload": incident.remediation.provider_payload,
          "provider_payload_updated_at": (
            incident.remediation.provider_payload_updated_at.isoformat()
            if incident.remediation.provider_payload_updated_at is not None
            else None
          ),
          "provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
        },
      }
    ).encode("utf-8")

  @staticmethod
  def _build_slack_payload(*, incident: OperatorIncidentEvent) -> bytes:
    return json.dumps(
      {
        "text": f"[{incident.severity.upper()}] {incident.summary}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": (
                f"*{incident.summary}*\n"
                f"{incident.detail}\n"
                f"`{incident.kind}` • `{incident.alert_id}` • `{incident.source}`"
                + (
                  f"\nRemediation: {incident.remediation.summary} "
                  f"(`{incident.remediation.runbook or 'n/a'}`)"
                  if incident.remediation.state != "not_applicable" and incident.remediation.summary
                  else ""
                )
              ),
            },
          }
        ],
      }
    ).encode("utf-8")

  def _build_pagerduty_payload(self, *, incident: OperatorIncidentEvent) -> bytes:
    event_action = "resolve" if incident.kind == "incident_resolved" else "trigger"
    return json.dumps(
      {
        "routing_key": self._pagerduty_integration_key,
        "event_action": event_action,
        "dedup_key": incident.alert_id,
        "payload": {
          "summary": incident.summary,
          "source": incident.source,
          "severity": self._map_pagerduty_severity(incident.severity),
          "timestamp": incident.timestamp.isoformat(),
          "custom_details": {
            "detail": incident.detail,
            "kind": incident.kind,
            "run_id": incident.run_id,
            "session_id": incident.session_id,
            "event_id": incident.event_id,
            "remediation_state": incident.remediation.state,
            "remediation_kind": incident.remediation.kind,
            "remediation_runbook": incident.remediation.runbook,
            "remediation_summary": incident.remediation.summary,
            "remediation_provider_payload": incident.remediation.provider_payload,
            "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
          },
        },
      }
    ).encode("utf-8")

  def _build_opsgenie_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    alias: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"GenieKey {self._opsgenie_api_key}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_alias = urllib_parse.quote(alias, safe="")
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_alias}/close?identifierType=alias",
        data=json.dumps(
          {
            "user": "Akra Trader",
            "source": incident.source,
            "note": incident.detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._opsgenie_api_url}/v2/alerts",
      data=json.dumps(
        {
          "message": incident.summary[:130],
          "alias": alias,
          "description": incident.detail,
          "source": incident.source,
          "priority": self._map_opsgenie_priority(incident.severity),
          "details": {
            "alert_id": incident.alert_id,
            "event_id": incident.event_id,
            "incident_kind": incident.kind,
            "run_id": incident.run_id,
            "session_id": incident.session_id,
            "remediation_state": incident.remediation.state,
            "remediation_kind": incident.remediation.kind,
            "remediation_runbook": incident.remediation.runbook,
            "remediation_summary": incident.remediation.summary,
            "remediation_provider_payload": incident.remediation.provider_payload,
            "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
          },
          "tags": ["akra", incident.source, incident.severity.lower()],
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_incidentio_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._incidentio_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": {"type": "application", "name": "Akra Trader"},
            "message": incident.detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._incidentio_api_url}/v2/incidents",
      data=json.dumps(
        {
          "incident": {
            "name": incident.summary[:255],
            "summary": incident.detail,
            "status": "active",
            "severity": self._map_incidentio_severity(incident.severity),
            "visibility": "public",
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_firehydrant_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._firehydrant_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._firehydrant_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "name": incident.summary[:255],
            "summary": incident.detail,
            "status": "open",
            "severity": self._map_firehydrant_severity(incident.severity),
            "priority": self._map_firehydrant_priority(incident.severity),
            "external_reference": reference,
            "details": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_rootly_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._rootly_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._rootly_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "title": incident.summary[:255],
            "summary": incident.detail,
            "status": "open",
            "severity_id": self._map_rootly_severity(incident.severity),
            "private": False,
            "slug": reference,
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_pagerduty_pull_request(
    self,
    *,
    workflow_reference: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(workflow_reference, safe="")
    return urllib_request.Request(
      f"https://api.pagerduty.com/incidents/{encoded_reference}",
      headers={
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Authorization": f"Token token={self._pagerduty_api_token}",
        "From": self._pagerduty_from_email or "",
      },
      method="GET",
    )

  def _build_incidentio_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._incidentio_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_firehydrant_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._firehydrant_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_rootly_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._rootly_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._rootly_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_blameless_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._blameless_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._blameless_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_xmatters_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._xmatters_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._xmatters_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_pagerduty_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    workflow_reference: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(workflow_reference, safe="")
    headers = {
      "Accept": "application/vnd.pagerduty+json;version=2",
      "Authorization": f"Token token={self._pagerduty_api_token}",
      "Content-Type": "application/json",
      "From": self._pagerduty_from_email or "",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}",
        data=json.dumps(
          {
            "incident": {
              "type": "incident_reference",
              "status": "acknowledged",
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}",
        data=json.dumps(
          {
            "incident": {
              "type": "incident_reference",
              "status": "resolved",
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}/notes",
        data=json.dumps(
          {
            "note": {
              "content": (
                f"Akra escalated incident to level {incident.escalation_level}. "
                f"Actor: {actor}. Detail: {detail}."
              ),
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}/notes",
        data=json.dumps(
          {
            "note": {
              "content": (
                f"Akra requested remediation. Actor: {actor}. "
                f"Summary: {incident.remediation.summary or incident.summary}. "
                f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
                f"{self._format_workflow_payload_context(payload)}"
              ),
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    raise ValueError(f"unsupported pagerduty workflow action: {action}")

  def _build_firehydrant_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._firehydrant_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported firehydrant workflow action: {action}")

  def _build_rootly_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._rootly_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported rootly workflow action: {action}")

  def _build_blameless_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._blameless_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._blameless_api_url}/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._blameless_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "title": incident.summary[:255],
            "summary": incident.detail,
            "status": "open",
            "severity": self._map_blameless_severity(incident.severity),
            "visibility": "private",
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_blameless_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._blameless_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._blameless_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._blameless_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._blameless_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._blameless_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported blameless workflow action: {action}")

  def _build_xmatters_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._xmatters_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._xmatters_api_url}/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._xmatters_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "title": incident.summary[:255],
            "summary": incident.detail,
            "status": "open",
            "priority": self._map_xmatters_priority(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_xmatters_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._xmatters_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._xmatters_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._xmatters_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._xmatters_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._xmatters_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported xmatters workflow action: {action}")

  def _build_servicenow_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._servicenow_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._servicenow_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_servicenow_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._servicenow_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._servicenow_api_url}/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._servicenow_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "short_description": incident.summary[:255],
            "description": incident.detail,
            "state": "new",
            "priority": self._map_servicenow_priority(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_servicenow_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._servicenow_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._servicenow_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._servicenow_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._servicenow_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._servicenow_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    raise ValueError(f"unsupported servicenow workflow action: {action}")

  def _build_squadcast_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._squadcast_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._squadcast_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_squadcast_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._squadcast_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._squadcast_api_url}/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._squadcast_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "severity": self._map_squadcast_severity(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_squadcast_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._squadcast_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._squadcast_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._squadcast_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._squadcast_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._squadcast_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported squadcast workflow action: {action}")

  def _build_bigpanda_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._bigpanda_api_url}/v2/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._bigpanda_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_bigpanda_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._bigpanda_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._bigpanda_api_url}/v2/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._bigpanda_api_url}/v2/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "severity": self._map_bigpanda_severity(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_bigpanda_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._bigpanda_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._bigpanda_api_url}/v2/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._bigpanda_api_url}/v2/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._bigpanda_api_url}/v2/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._bigpanda_api_url}/v2/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported bigpanda workflow action: {action}")

  def _build_grafana_oncall_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._grafana_oncall_api_url}/api/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._grafana_oncall_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_grafana_oncall_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._grafana_oncall_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._grafana_oncall_api_url}/api/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._grafana_oncall_api_url}/api/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "severity": self._map_grafana_oncall_severity(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_grafana_oncall_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._grafana_oncall_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._grafana_oncall_api_url}/api/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._grafana_oncall_api_url}/api/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._grafana_oncall_api_url}/api/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._grafana_oncall_api_url}/api/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported grafana_oncall workflow action: {action}")

  def _build_zenduty_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._zenduty_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_zenduty_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._zenduty_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._zenduty_api_url}/api/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "severity": self._map_zenduty_severity(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_zenduty_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._zenduty_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported zenduty workflow action: {action}")

  def _build_splunk_oncall_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._splunk_oncall_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_splunk_oncall_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._splunk_oncall_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._splunk_oncall_api_url}/api/v3/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "severity": self._map_splunk_oncall_severity(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_splunk_oncall_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._splunk_oncall_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported splunk_oncall workflow action: {action}")

  def _build_jira_service_management_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._jira_service_management_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_jira_service_management_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._jira_service_management_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._jira_service_management_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "priority": self._map_jira_service_management_priority(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_jira_service_management_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._jira_service_management_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported jira_service_management workflow action: {action}")

  def _build_pagertree_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._pagertree_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_pagertree_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._pagertree_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._pagertree_api_url}/api/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "urgency": self._map_pagertree_urgency(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_pagertree_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._pagertree_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported pagertree workflow action: {action}")

  def _build_alertops_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._alertops_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_alertops_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._alertops_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._alertops_api_url}/api/v2/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "priority": self._map_alertops_priority(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_alertops_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._alertops_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported alertops workflow action: {action}")

  def _build_signl4_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._signl4_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_signl4_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._signl4_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._signl4_api_url}/api/v1/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "priority": self._map_signl4_priority(incident.severity),
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_signl4_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._signl4_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported signl4 workflow action: {action}")

  def _build_ilert_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._ilert_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_ilert_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._ilert_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._ilert_api_url}/api/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._ilert_api_url}/api/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_ilert_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_ilert_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._ilert_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/accept{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
      method="PUT",
      )
    raise ValueError(f"unsupported ilert workflow action: {action}")

  def _build_betterstack_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._betterstack_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._betterstack_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_betterstack_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._betterstack_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._betterstack_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._betterstack_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_betterstack_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_betterstack_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._betterstack_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported betterstack workflow action: {action}")

  def _build_onpage_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._onpage_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._onpage_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_onpage_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._onpage_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._onpage_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._onpage_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_onpage_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_onpage_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._onpage_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
      method="PUT",
      )
    raise ValueError(f"unsupported onpage workflow action: {action}")

  def _build_allquiet_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._allquiet_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._allquiet_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_allquiet_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._allquiet_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._allquiet_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._allquiet_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_allquiet_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_allquiet_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._allquiet_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported allquiet workflow action: {action}")

  def _build_moogsoft_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._moogsoft_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_moogsoft_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._moogsoft_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._moogsoft_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._moogsoft_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_moogsoft_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_moogsoft_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._moogsoft_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported moogsoft workflow action: {action}")

  def _build_spikesh_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._spikesh_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._spikesh_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_spikesh_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._spikesh_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._spikesh_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._spikesh_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_spikesh_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_spikesh_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._spikesh_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
      headers=headers,
      method="PUT",
    )
    raise ValueError(f"unsupported spikesh workflow action: {action}")

  def _build_dutycalls_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._dutycalls_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_dutycalls_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._dutycalls_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._dutycalls_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._dutycalls_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_dutycalls_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_dutycalls_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._dutycalls_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
      headers=headers,
      method="PUT",
    )
    raise ValueError(f"unsupported dutycalls workflow action: {action}")

  def _build_incidenthub_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._incidenthub_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_opsramp_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._opsramp_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._opsramp_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_resolver_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._resolver_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._resolver_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_openduty_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._openduty_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._openduty_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_cabot_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._cabot_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._cabot_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_haloitsm_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._haloitsm_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_incidentmanagerio_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._incidentmanagerio_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_oneuptime_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._oneuptime_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_squzy_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._squzy_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._squzy_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_incidenthub_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._incidenthub_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._incidenthub_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._incidenthub_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_incidenthub_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_resolver_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._resolver_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._resolver_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._resolver_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_resolver_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_openduty_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._openduty_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._openduty_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._openduty_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_openduty_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_cabot_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._cabot_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._cabot_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._cabot_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_cabot_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_haloitsm_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._haloitsm_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._haloitsm_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._haloitsm_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_haloitsm_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_incidentmanagerio_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._incidentmanagerio_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._incidentmanagerio_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_incidentmanagerio_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_oneuptime_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._oneuptime_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._oneuptime_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._oneuptime_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_oneuptime_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_squzy_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._squzy_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._squzy_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._squzy_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_squzy_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_opsramp_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._opsramp_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._opsramp_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._opsramp_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_opsramp_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_incidenthub_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._incidenthub_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
    )
    raise ValueError(f"unsupported incidenthub workflow action: {action}")

  def _build_resolver_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._resolver_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._resolver_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._resolver_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._resolver_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._resolver_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported resolver workflow action: {action}")

  def _build_openduty_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._openduty_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._openduty_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._openduty_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._openduty_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._openduty_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported openduty workflow action: {action}")

  def _build_cabot_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._cabot_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._cabot_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._cabot_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._cabot_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._cabot_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported cabot workflow action: {action}")

  def _build_haloitsm_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._haloitsm_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported haloitsm workflow action: {action}")

  def _build_incidentmanagerio_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._incidentmanagerio_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported incidentmanagerio workflow action: {action}")

  def _build_oneuptime_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._oneuptime_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported oneuptime workflow action: {action}")

  def _build_squzy_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._squzy_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._squzy_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._squzy_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._squzy_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._squzy_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported squzy workflow action: {action}")

  def _build_opsramp_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._opsramp_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported opsramp workflow action: {action}")

  def _build_opsgenie_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}?identifierType={reference_type}",
      headers={
        "Authorization": f"GenieKey {self._opsgenie_api_key}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_opsgenie_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifierType={reference_type}"
    headers = {
      "Authorization": f"GenieKey {self._opsgenie_api_key}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/close{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/notes{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/notes{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported opsgenie workflow action: {action}")

  def _build_incidentio_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._incidentio_api_token}",
      "Content-Type": "application/json",
    }
    base_payload = {
      "actor": {"type": "application", "name": actor},
      "message": detail,
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/acknowledge{suffix}",
        data=json.dumps(base_payload).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/resolve{suffix}",
        data=json.dumps(
          {
            **base_payload,
            "message": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/escalate{suffix}",
        data=json.dumps(
          {
            **base_payload,
            "message": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/remediate{suffix}",
        data=json.dumps(
          {
            **base_payload,
            "message": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported incidentio workflow action: {action}")

  @staticmethod
  def _read_json_response(response: object) -> dict[str, Any]:
    if not hasattr(response, "read"):
      return {}
    raw = response.read()
    if isinstance(raw, bytes):
      body = raw.decode("utf-8")
    elif isinstance(raw, str):
      body = raw
    else:
      body = ""
    if not body:
      return {}
    parsed = json.loads(body)
    return parsed if isinstance(parsed, dict) else {}

  @staticmethod
  def _extract_mapping(*candidates: Any) -> dict[str, Any]:
    for candidate in candidates:
      if isinstance(candidate, dict):
        return candidate
    return {}

  @staticmethod
  def _extract_string_list(*candidates: Any) -> list[str]:
    for candidate in candidates:
      if isinstance(candidate, str):
        value = candidate.strip()
        if value:
          return [value]
      elif isinstance(candidate, (list, tuple)):
        values = [
          str(item).strip()
          for item in candidate
          if isinstance(item, str) and item.strip()
        ]
        if values:
          return values
    return []

  @staticmethod
  def _first_non_empty_string(*candidates: Any) -> str | None:
    for candidate in candidates:
      if isinstance(candidate, str):
        value = candidate.strip()
        if value:
          return value
    return None

  @staticmethod
  def _parse_provider_datetime(*candidates: Any) -> datetime | None:
    for candidate in candidates:
      if isinstance(candidate, datetime):
        return candidate.astimezone(UTC) if candidate.tzinfo is not None else candidate.replace(tzinfo=UTC)
      if not isinstance(candidate, str):
        continue
      value = candidate.strip()
      if not value:
        continue
      normalized = value.replace("Z", "+00:00")
      try:
        parsed = datetime.fromisoformat(normalized)
      except ValueError:
        continue
      return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    return None

  @staticmethod
  def _format_workflow_payload_context(payload: dict[str, Any] | None) -> str:
    if not payload:
      return ""
    return f" Context: {json.dumps(payload, default=str, sort_keys=True)}"

  @staticmethod
  def _map_pagerduty_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"

  @staticmethod
  def _map_opsgenie_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "P1"
    if normalized in {"warning", "warn"}:
      return "P3"
    return "P5"

  @staticmethod
  def _map_incidentio_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"

  @staticmethod
  def _map_firehydrant_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "SEV1"
    if normalized in {"warning", "warn"}:
      return "SEV3"
    return "SEV4"

  @staticmethod
  def _map_firehydrant_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "P1"
    if normalized in {"warning", "warn"}:
      return "P2"
    return "P3"

  @staticmethod
  def _map_rootly_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "sev_critical"
    if normalized in {"warning", "warn"}:
      return "sev_warning"
    return "sev_info"

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
