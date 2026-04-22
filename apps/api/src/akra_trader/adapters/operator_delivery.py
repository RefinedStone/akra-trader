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

from akra_trader.adapters.operator_delivery_core_providers import CoreWorkflowProviderMixin
from akra_trader.adapters.operator_delivery_phase_resolvers import OperatorDeliveryPhaseResolverMixin
from akra_trader.adapters.operator_delivery_workflow_providers_group_one import OperatorDeliveryWorkflowProvidersGroupOneMixin
from akra_trader.adapters.operator_delivery_workflow_providers_group_two import OperatorDeliveryWorkflowProvidersGroupTwoMixin
from akra_trader.adapters.operator_delivery_workflow_providers_group_three import OperatorDeliveryWorkflowProvidersGroupThreeMixin
from akra_trader.adapters.operator_delivery_workflow_providers_group_four import OperatorDeliveryWorkflowProvidersGroupFourMixin
from akra_trader.adapters.operator_delivery_recovery_engine_requests import OperatorDeliveryRecoveryEngineRequestMixin
from akra_trader.adapters.operator_delivery_shared_helpers import OperatorDeliverySharedHelpersMixin
from akra_trader.adapters.operator_delivery_registry import list_enabled_workflow_providers
from akra_trader.adapters.operator_delivery_registry import normalize_delivery_target
from akra_trader.adapters.operator_delivery_registry import normalize_workflow_provider
from akra_trader.adapters.operator_delivery_registry import resolve_delivery_handler
from akra_trader.adapters.operator_delivery_registry import resolve_workflow_pull_handler
from akra_trader.adapters.operator_delivery_registry import resolve_workflow_sync_handler
from akra_trader.domain.models import OperatorAlertPrimaryFocus
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.ports import OperatorAlertDeliveryPort


LOGGER = logging.getLogger("akra_trader.operator_delivery")


def _normalize_target(target: str) -> str | None:
  return normalize_delivery_target(target)


class OperatorAlertDeliveryAdapter(
  OperatorDeliverySharedHelpersMixin,
  OperatorDeliveryWorkflowProvidersGroupFourMixin,
  OperatorDeliveryWorkflowProvidersGroupThreeMixin,
  OperatorDeliveryWorkflowProvidersGroupTwoMixin,
  OperatorDeliveryWorkflowProvidersGroupOneMixin,
  OperatorDeliveryRecoveryEngineRequestMixin,
  OperatorDeliveryPhaseResolverMixin,
  CoreWorkflowProviderMixin,
  OperatorAlertDeliveryPort,
):
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
    crisescontrol_api_token: str | None = None,
    crisescontrol_api_url: str = "https://api.crises-control.com/v1",
    crisescontrol_recovery_engine_url_template: str | None = None,
    crisescontrol_recovery_engine_token: str | None = None,
    freshservice_api_token: str | None = None,
    freshservice_api_url: str = "https://api.freshservice.com/v2",
    freshservice_recovery_engine_url_template: str | None = None,
    freshservice_recovery_engine_token: str | None = None,
    freshdesk_api_token: str | None = None,
    freshdesk_api_url: str = "https://api.freshdesk.com/v2",
    freshdesk_recovery_engine_url_template: str | None = None,
    freshdesk_recovery_engine_token: str | None = None,
    happyfox_api_token: str | None = None,
    happyfox_api_url: str = "https://api.happyfox.com/v1",
    happyfox_recovery_engine_url_template: str | None = None,
    happyfox_recovery_engine_token: str | None = None,
    zendesk_api_token: str | None = None,
    zendesk_api_url: str = "https://api.zendesk.com/api/v2",
    zendesk_recovery_engine_url_template: str | None = None,
    zendesk_recovery_engine_token: str | None = None,
    zohodesk_api_token: str | None = None,
    zohodesk_api_url: str = "https://desk.zoho.com/api/v1",
    zohodesk_recovery_engine_url_template: str | None = None,
    zohodesk_recovery_engine_token: str | None = None,
    helpscout_api_token: str | None = None,
    helpscout_api_url: str = "https://api.helpscout.net/v2",
    helpscout_recovery_engine_url_template: str | None = None,
    helpscout_recovery_engine_token: str | None = None,
    kayako_api_token: str | None = None,
    kayako_api_url: str = "https://api.kayako.com/v1",
    kayako_recovery_engine_url_template: str | None = None,
    kayako_recovery_engine_token: str | None = None,
    intercom_api_token: str | None = None,
    intercom_api_url: str = "https://api.intercom.io",
    intercom_recovery_engine_url_template: str | None = None,
    intercom_recovery_engine_token: str | None = None,
    front_api_token: str | None = None,
    front_api_url: str = "https://api2.frontapp.com",
    front_recovery_engine_url_template: str | None = None,
    front_recovery_engine_token: str | None = None,
    servicedeskplus_api_token: str | None = None,
    servicedeskplus_api_url: str = "https://api.manageengine.com/servicedeskplus/v3",
    servicedeskplus_recovery_engine_url_template: str | None = None,
    servicedeskplus_recovery_engine_token: str | None = None,
    sysaid_api_token: str | None = None,
    sysaid_api_url: str = "https://api.sysaid.com/v1",
    sysaid_recovery_engine_url_template: str | None = None,
    sysaid_recovery_engine_token: str | None = None,
    bmchelix_api_token: str | None = None,
    bmchelix_api_url: str = "https://api.bmchelix.com/v1",
    bmchelix_recovery_engine_url_template: str | None = None,
    bmchelix_recovery_engine_token: str | None = None,
    solarwindsservicedesk_api_token: str | None = None,
    solarwindsservicedesk_api_url: str = "https://api.solarwinds.com/servicedesk/v1",
    solarwindsservicedesk_recovery_engine_url_template: str | None = None,
    solarwindsservicedesk_recovery_engine_token: str | None = None,
    topdesk_api_token: str | None = None,
    topdesk_api_url: str = "https://api.topdesk.com/tas/api",
    topdesk_recovery_engine_url_template: str | None = None,
    topdesk_recovery_engine_token: str | None = None,
    invgateservicedesk_api_token: str | None = None,
    invgateservicedesk_api_url: str = "https://api.invgate.com/service-desk/v1",
    invgateservicedesk_recovery_engine_url_template: str | None = None,
    invgateservicedesk_recovery_engine_token: str | None = None,
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
    self._crisescontrol_api_token = crisescontrol_api_token
    self._crisescontrol_api_url = crisescontrol_api_url.rstrip("/")
    self._crisescontrol_recovery_engine_url_template = crisescontrol_recovery_engine_url_template
    self._crisescontrol_recovery_engine_token = crisescontrol_recovery_engine_token
    self._freshservice_api_token = freshservice_api_token
    self._freshservice_api_url = freshservice_api_url.rstrip("/")
    self._freshservice_recovery_engine_url_template = freshservice_recovery_engine_url_template
    self._freshservice_recovery_engine_token = freshservice_recovery_engine_token
    self._freshdesk_api_token = freshdesk_api_token
    self._freshdesk_api_url = freshdesk_api_url.rstrip("/")
    self._freshdesk_recovery_engine_url_template = freshdesk_recovery_engine_url_template
    self._freshdesk_recovery_engine_token = freshdesk_recovery_engine_token
    self._happyfox_api_token = happyfox_api_token
    self._happyfox_api_url = happyfox_api_url.rstrip("/")
    self._happyfox_recovery_engine_url_template = happyfox_recovery_engine_url_template
    self._happyfox_recovery_engine_token = happyfox_recovery_engine_token
    self._zendesk_api_token = zendesk_api_token
    self._zendesk_api_url = zendesk_api_url.rstrip("/")
    self._zendesk_recovery_engine_url_template = zendesk_recovery_engine_url_template
    self._zendesk_recovery_engine_token = zendesk_recovery_engine_token
    self._zohodesk_api_token = zohodesk_api_token
    self._zohodesk_api_url = zohodesk_api_url.rstrip("/")
    self._zohodesk_recovery_engine_url_template = zohodesk_recovery_engine_url_template
    self._zohodesk_recovery_engine_token = zohodesk_recovery_engine_token
    self._helpscout_api_token = helpscout_api_token
    self._helpscout_api_url = helpscout_api_url.rstrip("/")
    self._helpscout_recovery_engine_url_template = helpscout_recovery_engine_url_template
    self._helpscout_recovery_engine_token = helpscout_recovery_engine_token
    self._kayako_api_token = kayako_api_token
    self._kayako_api_url = kayako_api_url.rstrip("/")
    self._kayako_recovery_engine_url_template = kayako_recovery_engine_url_template
    self._kayako_recovery_engine_token = kayako_recovery_engine_token
    self._intercom_api_token = intercom_api_token
    self._intercom_api_url = intercom_api_url.rstrip("/")
    self._intercom_recovery_engine_url_template = intercom_recovery_engine_url_template
    self._intercom_recovery_engine_token = intercom_recovery_engine_token
    self._front_api_token = front_api_token
    self._front_api_url = front_api_url.rstrip("/")
    self._front_recovery_engine_url_template = front_recovery_engine_url_template
    self._front_recovery_engine_token = front_recovery_engine_token
    self._servicedeskplus_api_token = servicedeskplus_api_token
    self._servicedeskplus_api_url = servicedeskplus_api_url.rstrip("/")
    self._servicedeskplus_recovery_engine_url_template = servicedeskplus_recovery_engine_url_template
    self._servicedeskplus_recovery_engine_token = servicedeskplus_recovery_engine_token
    self._sysaid_api_token = sysaid_api_token
    self._sysaid_api_url = sysaid_api_url.rstrip("/")
    self._sysaid_recovery_engine_url_template = sysaid_recovery_engine_url_template
    self._sysaid_recovery_engine_token = sysaid_recovery_engine_token
    self._bmchelix_api_token = bmchelix_api_token
    self._bmchelix_api_url = bmchelix_api_url.rstrip("/")
    self._bmchelix_recovery_engine_url_template = bmchelix_recovery_engine_url_template
    self._bmchelix_recovery_engine_token = bmchelix_recovery_engine_token
    self._solarwindsservicedesk_api_token = solarwindsservicedesk_api_token
    self._solarwindsservicedesk_api_url = solarwindsservicedesk_api_url.rstrip("/")
    self._solarwindsservicedesk_recovery_engine_url_template = (
      solarwindsservicedesk_recovery_engine_url_template
    )
    self._solarwindsservicedesk_recovery_engine_token = solarwindsservicedesk_recovery_engine_token
    self._topdesk_api_token = topdesk_api_token
    self._topdesk_api_url = topdesk_api_url.rstrip("/")
    self._topdesk_recovery_engine_url_template = topdesk_recovery_engine_url_template
    self._topdesk_recovery_engine_token = topdesk_recovery_engine_token
    self._invgateservicedesk_api_token = invgateservicedesk_api_token
    self._invgateservicedesk_api_url = invgateservicedesk_api_url.rstrip("/")
    self._invgateservicedesk_recovery_engine_url_template = (
      invgateservicedesk_recovery_engine_url_template
    )
    self._invgateservicedesk_recovery_engine_token = invgateservicedesk_recovery_engine_token
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
    return list_enabled_workflow_providers(self)

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
      handler = resolve_delivery_handler(self, target)
      if handler is None:
        continue
      records.append(handler(incident=incident, attempt_number=attempt_number, phase=phase))
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
    normalized_provider = normalize_workflow_provider(provider)
    normalized_action = action.strip().lower().replace("-", "_")
    handler = resolve_workflow_sync_handler(self, normalized_provider)
    if handler is not None:
      return (
        handler(
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
    normalized_provider = normalize_workflow_provider(provider)
    handler = resolve_workflow_pull_handler(self, normalized_provider)
    if handler is None:
      return None
    return handler(incident=incident)

