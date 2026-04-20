from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class DeliveryTargetSpec:
  target_key: str
  aliases: tuple[str, ...]
  deliver_method_name: str
  provider_key: str | None = None


@dataclass(frozen=True)
class WorkflowProviderSpec:
  provider_key: str
  required_attrs: tuple[str, ...]
  sync_method_name: str
  pull_method_name: str


DELIVERY_TARGET_SPECS: tuple[DeliveryTargetSpec, ...] = (
  DeliveryTargetSpec("operator_console", ("console", "operator_console"), "_deliver_console"),
  DeliveryTargetSpec("operator_webhook", ("webhook", "operator_webhook"), "_deliver_webhook"),
  DeliveryTargetSpec("slack_webhook", ("slack", "slack_webhook", "operator_slack"), "_deliver_slack"),
  DeliveryTargetSpec(
    "pagerduty_events",
    ("pagerduty", "pagerduty_events", "operator_pagerduty"),
    "_deliver_pagerduty",
    provider_key="pagerduty",
  ),
  DeliveryTargetSpec(
    "incidentio_incidents",
    ("incidentio", "incident_io", "incidentio_incidents", "operator_incidentio"),
    "_deliver_incidentio",
    provider_key="incidentio",
  ),
  DeliveryTargetSpec(
    "firehydrant_incidents",
    ("firehydrant", "fire_hydrant", "firehydrant_incidents", "operator_firehydrant"),
    "_deliver_firehydrant",
    provider_key="firehydrant",
  ),
  DeliveryTargetSpec("rootly_incidents", ("rootly", "root_ly", "rootly_incidents", "operator_rootly"), "_deliver_rootly", provider_key="rootly"),
  DeliveryTargetSpec("blameless_incidents", ("blameless", "blameless_incidents", "operator_blameless"), "_deliver_blameless", provider_key="blameless"),
  DeliveryTargetSpec("xmatters_incidents", ("xmatters", "x_matters", "xmatters_incidents", "operator_xmatters"), "_deliver_xmatters", provider_key="xmatters"),
  DeliveryTargetSpec("servicenow_incidents", ("servicenow", "service_now", "servicenow_incidents", "operator_servicenow"), "_deliver_servicenow", provider_key="servicenow"),
  DeliveryTargetSpec("squadcast_incidents", ("squadcast", "squad_cast", "squadcast_incidents", "operator_squadcast"), "_deliver_squadcast", provider_key="squadcast"),
  DeliveryTargetSpec("bigpanda_incidents", ("bigpanda", "big_panda", "bigpanda_incidents", "operator_bigpanda"), "_deliver_bigpanda", provider_key="bigpanda"),
  DeliveryTargetSpec(
    "grafana_oncall_incidents",
    ("grafanaoncall", "grafana_oncall", "grafana_oncall_incidents", "operator_grafana_oncall"),
    "_deliver_grafana_oncall",
    provider_key="grafana_oncall",
  ),
  DeliveryTargetSpec("zenduty_incidents", ("zenduty", "zen_duty", "zenduty_incidents", "operator_zenduty"), "_deliver_zenduty", provider_key="zenduty"),
  DeliveryTargetSpec(
    "splunk_oncall_incidents",
    ("splunk_oncall", "splunkoncall", "splunk_oncall_incidents", "victorops", "operator_splunk_oncall"),
    "_deliver_splunk_oncall",
    provider_key="splunk_oncall",
  ),
  DeliveryTargetSpec(
    "jira_service_management_incidents",
    ("jira_service_management", "jira_service_management_incidents", "jsm", "jsm_incidents", "jira_service_desk", "jira_service_desk_incidents", "operator_jira_service_management"),
    "_deliver_jira_service_management",
    provider_key="jira_service_management",
  ),
  DeliveryTargetSpec("pagertree_incidents", ("pagertree", "pager_tree", "pagertree_incidents", "operator_pagertree"), "_deliver_pagertree", provider_key="pagertree"),
  DeliveryTargetSpec("alertops_incidents", ("alertops", "alert_ops", "alertops_incidents", "operator_alertops"), "_deliver_alertops", provider_key="alertops"),
  DeliveryTargetSpec("signl4_incidents", ("signl4", "signl_4", "signl4_incidents", "operator_signl4"), "_deliver_signl4", provider_key="signl4"),
  DeliveryTargetSpec("ilert_incidents", ("ilert", "i_lert", "ilert_incidents", "ilert_alerts", "operator_ilert"), "_deliver_ilert", provider_key="ilert"),
  DeliveryTargetSpec("betterstack_incidents", ("betterstack", "better_stack", "betterstack_incidents", "betterstack_alerts", "operator_betterstack"), "_deliver_betterstack", provider_key="betterstack"),
  DeliveryTargetSpec("onpage_incidents", ("onpage", "on_page", "onpage_incidents", "onpage_alerts", "operator_onpage"), "_deliver_onpage", provider_key="onpage"),
  DeliveryTargetSpec("allquiet_incidents", ("allquiet", "all_quiet", "allquiet_incidents", "allquiet_alerts", "operator_allquiet"), "_deliver_allquiet", provider_key="allquiet"),
  DeliveryTargetSpec("moogsoft_incidents", ("moogsoft", "moogsoft_incidents", "moogsoft_alerts", "operator_moogsoft"), "_deliver_moogsoft", provider_key="moogsoft"),
  DeliveryTargetSpec("spikesh_incidents", ("spikesh", "spike_sh", "spikesh_incidents", "spikesh_alerts", "operator_spikesh"), "_deliver_spikesh", provider_key="spikesh"),
  DeliveryTargetSpec("dutycalls_incidents", ("dutycalls", "duty_calls", "dutycalls_incidents", "dutycalls_alerts", "operator_dutycalls"), "_deliver_dutycalls", provider_key="dutycalls"),
  DeliveryTargetSpec("incidenthub_incidents", ("incidenthub", "incident_hub", "incidenthub_incidents", "incidenthub_alerts", "operator_incidenthub"), "_deliver_incidenthub", provider_key="incidenthub"),
  DeliveryTargetSpec("resolver_incidents", ("resolver", "resolver_incidents", "resolver_alerts", "operator_resolver"), "_deliver_resolver", provider_key="resolver"),
  DeliveryTargetSpec("openduty_incidents", ("openduty", "open_duty", "openduty_incidents", "openduty_alerts", "operator_openduty"), "_deliver_openduty", provider_key="openduty"),
  DeliveryTargetSpec("cabot_incidents", ("cabot", "cabot_incidents", "cabot_alerts", "operator_cabot"), "_deliver_cabot", provider_key="cabot"),
  DeliveryTargetSpec("haloitsm_incidents", ("haloitsm", "halo_itsm", "haloitsm_incidents", "haloitsm_alerts", "operator_haloitsm"), "_deliver_haloitsm", provider_key="haloitsm"),
  DeliveryTargetSpec("incidentmanagerio_incidents", ("incidentmanagerio", "incidentmanager_io", "incidentmanagerio_incidents", "incidentmanagerio_alerts", "operator_incidentmanagerio"), "_deliver_incidentmanagerio", provider_key="incidentmanagerio"),
  DeliveryTargetSpec("oneuptime_incidents", ("oneuptime", "one_uptime", "oneuptime_incidents", "oneuptime_alerts", "operator_oneuptime"), "_deliver_oneuptime", provider_key="oneuptime"),
  DeliveryTargetSpec("squzy_incidents", ("squzy", "squzy_incidents", "squzy_alerts", "operator_squzy"), "_deliver_squzy", provider_key="squzy"),
  DeliveryTargetSpec("crisescontrol_incidents", ("crisescontrol", "crises_control", "crisescontrol_incidents", "crisescontrol_alerts", "operator_crisescontrol"), "_deliver_crisescontrol", provider_key="crisescontrol"),
  DeliveryTargetSpec("freshservice_incidents", ("freshservice", "fresh_service", "freshservice_incidents", "freshservice_alerts", "operator_freshservice"), "_deliver_freshservice", provider_key="freshservice"),
  DeliveryTargetSpec("freshdesk_incidents", ("freshdesk", "fresh_desk", "freshdesk_incidents", "freshdesk_alerts", "operator_freshdesk"), "_deliver_freshdesk", provider_key="freshdesk"),
  DeliveryTargetSpec("happyfox_incidents", ("happyfox", "happy_fox", "happyfox_incidents", "happyfox_alerts", "operator_happyfox"), "_deliver_happyfox", provider_key="happyfox"),
  DeliveryTargetSpec("zendesk_incidents", ("zendesk", "zendesk_incidents", "zendesk_alerts", "operator_zendesk"), "_deliver_zendesk", provider_key="zendesk"),
  DeliveryTargetSpec("zohodesk_incidents", ("zohodesk", "zoho_desk", "zohodesk_incidents", "zohodesk_alerts", "operator_zohodesk"), "_deliver_zohodesk", provider_key="zohodesk"),
  DeliveryTargetSpec("helpscout_incidents", ("helpscout", "help_scout", "helpscout_incidents", "helpscout_alerts", "operator_helpscout"), "_deliver_helpscout", provider_key="helpscout"),
  DeliveryTargetSpec("kayako_incidents", ("kayako", "kayako_incidents", "kayako_alerts", "operator_kayako"), "_deliver_kayako", provider_key="kayako"),
  DeliveryTargetSpec("intercom_incidents", ("intercom", "intercom_incidents", "intercom_alerts", "operator_intercom"), "_deliver_intercom", provider_key="intercom"),
  DeliveryTargetSpec("front_incidents", ("front", "front_incidents", "front_alerts", "operator_front"), "_deliver_front", provider_key="front"),
  DeliveryTargetSpec("servicedeskplus_incidents", ("servicedeskplus", "service_desk_plus", "manageengine_servicedesk_plus", "servicedeskplus_incidents", "servicedeskplus_alerts", "operator_servicedeskplus"), "_deliver_servicedeskplus", provider_key="servicedeskplus"),
  DeliveryTargetSpec("sysaid_incidents", ("sysaid", "sys_aid", "sysaid_incidents", "sysaid_alerts", "operator_sysaid"), "_deliver_sysaid", provider_key="sysaid"),
  DeliveryTargetSpec("bmchelix_incidents", ("bmchelix", "bmc_helix", "bmchelix_incidents", "bmchelix_alerts", "operator_bmchelix"), "_deliver_bmchelix", provider_key="bmchelix"),
  DeliveryTargetSpec("solarwindsservicedesk_incidents", ("solarwindsservicedesk", "solarwinds_service_desk", "solarwindsservicedesk_incidents", "solarwindsservicedesk_alerts", "operator_solarwindsservicedesk"), "_deliver_solarwindsservicedesk", provider_key="solarwindsservicedesk"),
  DeliveryTargetSpec("topdesk_incidents", ("topdesk", "topdesk_incidents", "topdesk_alerts", "operator_topdesk"), "_deliver_topdesk", provider_key="topdesk"),
  DeliveryTargetSpec("invgateservicedesk_incidents", ("invgateservicedesk", "invgate_service_desk", "invgate_servicedesk", "invgateservicedesk_incidents", "invgateservicedesk_alerts", "operator_invgateservicedesk"), "_deliver_invgateservicedesk", provider_key="invgateservicedesk"),
  DeliveryTargetSpec("opsramp_incidents", ("opsramp", "ops_ramp", "opsramp_incidents", "opsramp_alerts", "operator_opsramp"), "_deliver_opsramp", provider_key="opsramp"),
  DeliveryTargetSpec("opsgenie_alerts", ("opsgenie", "opsgenie_alerts", "operator_opsgenie"), "_deliver_opsgenie", provider_key="opsgenie"),
)

WORKFLOW_PROVIDER_SPECS: tuple[WorkflowProviderSpec, ...] = (
  WorkflowProviderSpec("pagerduty", ("_pagerduty_api_token", "_pagerduty_from_email"), "_sync_pagerduty_workflow", "_pull_pagerduty_workflow_state"),
  WorkflowProviderSpec("incidentio", ("_incidentio_api_token",), "_sync_incidentio_workflow", "_pull_incidentio_workflow_state"),
  WorkflowProviderSpec("firehydrant", ("_firehydrant_api_token",), "_sync_firehydrant_workflow", "_pull_firehydrant_workflow_state"),
  WorkflowProviderSpec("rootly", ("_rootly_api_token",), "_sync_rootly_workflow", "_pull_rootly_workflow_state"),
  WorkflowProviderSpec("blameless", ("_blameless_api_token",), "_sync_blameless_workflow", "_pull_blameless_workflow_state"),
  WorkflowProviderSpec("xmatters", ("_xmatters_api_token",), "_sync_xmatters_workflow", "_pull_xmatters_workflow_state"),
  WorkflowProviderSpec("servicenow", ("_servicenow_api_token",), "_sync_servicenow_workflow", "_pull_servicenow_workflow_state"),
  WorkflowProviderSpec("squadcast", ("_squadcast_api_token",), "_sync_squadcast_workflow", "_pull_squadcast_workflow_state"),
  WorkflowProviderSpec("bigpanda", ("_bigpanda_api_token",), "_sync_bigpanda_workflow", "_pull_bigpanda_workflow_state"),
  WorkflowProviderSpec("grafana_oncall", ("_grafana_oncall_api_token",), "_sync_grafana_oncall_workflow", "_pull_grafana_oncall_workflow_state"),
  WorkflowProviderSpec("zenduty", ("_zenduty_api_token",), "_sync_zenduty_workflow", "_pull_zenduty_workflow_state"),
  WorkflowProviderSpec("splunk_oncall", ("_splunk_oncall_api_token",), "_sync_splunk_oncall_workflow", "_pull_splunk_oncall_workflow_state"),
  WorkflowProviderSpec("jira_service_management", ("_jira_service_management_api_token",), "_sync_jira_service_management_workflow", "_pull_jira_service_management_workflow_state"),
  WorkflowProviderSpec("pagertree", ("_pagertree_api_token",), "_sync_pagertree_workflow", "_pull_pagertree_workflow_state"),
  WorkflowProviderSpec("alertops", ("_alertops_api_token",), "_sync_alertops_workflow", "_pull_alertops_workflow_state"),
  WorkflowProviderSpec("signl4", ("_signl4_api_token",), "_sync_signl4_workflow", "_pull_signl4_workflow_state"),
  WorkflowProviderSpec("ilert", ("_ilert_api_token",), "_sync_ilert_workflow", "_pull_ilert_workflow_state"),
  WorkflowProviderSpec("betterstack", ("_betterstack_api_token",), "_sync_betterstack_workflow", "_pull_betterstack_workflow_state"),
  WorkflowProviderSpec("onpage", ("_onpage_api_token",), "_sync_onpage_workflow", "_pull_onpage_workflow_state"),
  WorkflowProviderSpec("allquiet", ("_allquiet_api_token",), "_sync_allquiet_workflow", "_pull_allquiet_workflow_state"),
  WorkflowProviderSpec("moogsoft", ("_moogsoft_api_token",), "_sync_moogsoft_workflow", "_pull_moogsoft_workflow_state"),
  WorkflowProviderSpec("spikesh", ("_spikesh_api_token",), "_sync_spikesh_workflow", "_pull_spikesh_workflow_state"),
  WorkflowProviderSpec("dutycalls", ("_dutycalls_api_token",), "_sync_dutycalls_workflow", "_pull_dutycalls_workflow_state"),
  WorkflowProviderSpec("incidenthub", ("_incidenthub_api_token",), "_sync_incidenthub_workflow", "_pull_incidenthub_workflow_state"),
  WorkflowProviderSpec("resolver", ("_resolver_api_token",), "_sync_resolver_workflow", "_pull_resolver_workflow_state"),
  WorkflowProviderSpec("openduty", ("_openduty_api_token",), "_sync_openduty_workflow", "_pull_openduty_workflow_state"),
  WorkflowProviderSpec("cabot", ("_cabot_api_token",), "_sync_cabot_workflow", "_pull_cabot_workflow_state"),
  WorkflowProviderSpec("haloitsm", ("_haloitsm_api_token",), "_sync_haloitsm_workflow", "_pull_haloitsm_workflow_state"),
  WorkflowProviderSpec("incidentmanagerio", ("_incidentmanagerio_api_token",), "_sync_incidentmanagerio_workflow", "_pull_incidentmanagerio_workflow_state"),
  WorkflowProviderSpec("oneuptime", ("_oneuptime_api_token",), "_sync_oneuptime_workflow", "_pull_oneuptime_workflow_state"),
  WorkflowProviderSpec("squzy", ("_squzy_api_token",), "_sync_squzy_workflow", "_pull_squzy_workflow_state"),
  WorkflowProviderSpec("crisescontrol", ("_crisescontrol_api_token",), "_sync_crisescontrol_workflow", "_pull_crisescontrol_workflow_state"),
  WorkflowProviderSpec("freshservice", ("_freshservice_api_token",), "_sync_freshservice_workflow", "_pull_freshservice_workflow_state"),
  WorkflowProviderSpec("freshdesk", ("_freshdesk_api_token",), "_sync_freshdesk_workflow", "_pull_freshdesk_workflow_state"),
  WorkflowProviderSpec("happyfox", ("_happyfox_api_token",), "_sync_happyfox_workflow", "_pull_happyfox_workflow_state"),
  WorkflowProviderSpec("zendesk", ("_zendesk_api_token",), "_sync_zendesk_workflow", "_pull_zendesk_workflow_state"),
  WorkflowProviderSpec("zohodesk", ("_zohodesk_api_token",), "_sync_zohodesk_workflow", "_pull_zohodesk_workflow_state"),
  WorkflowProviderSpec("helpscout", ("_helpscout_api_token",), "_sync_helpscout_workflow", "_pull_helpscout_workflow_state"),
  WorkflowProviderSpec("kayako", ("_kayako_api_token",), "_sync_kayako_workflow", "_pull_kayako_workflow_state"),
  WorkflowProviderSpec("intercom", ("_intercom_api_token",), "_sync_intercom_workflow", "_pull_intercom_workflow_state"),
  WorkflowProviderSpec("front", ("_front_api_token",), "_sync_front_workflow", "_pull_front_workflow_state"),
  WorkflowProviderSpec("servicedeskplus", ("_servicedeskplus_api_token",), "_sync_servicedeskplus_workflow", "_pull_servicedeskplus_workflow_state"),
  WorkflowProviderSpec("sysaid", ("_sysaid_api_token",), "_sync_sysaid_workflow", "_pull_sysaid_workflow_state"),
  WorkflowProviderSpec("bmchelix", ("_bmchelix_api_token",), "_sync_bmchelix_workflow", "_pull_bmchelix_workflow_state"),
  WorkflowProviderSpec("solarwindsservicedesk", ("_solarwindsservicedesk_api_token",), "_sync_solarwindsservicedesk_workflow", "_pull_solarwindsservicedesk_workflow_state"),
  WorkflowProviderSpec("topdesk", ("_topdesk_api_token",), "_sync_topdesk_workflow", "_pull_topdesk_workflow_state"),
  WorkflowProviderSpec("invgateservicedesk", ("_invgateservicedesk_api_token",), "_sync_invgateservicedesk_workflow", "_pull_invgateservicedesk_workflow_state"),
  WorkflowProviderSpec("opsramp", ("_opsramp_api_token",), "_sync_opsramp_workflow", "_pull_opsramp_workflow_state"),
  WorkflowProviderSpec("opsgenie", ("_opsgenie_api_key",), "_sync_opsgenie_workflow", "_pull_opsgenie_workflow_state"),
)

DELIVERY_TARGET_SPEC_BY_KEY = {
  spec.target_key: spec
  for spec in DELIVERY_TARGET_SPECS
}

DELIVERY_TARGET_ALIAS_TO_KEY = {
  alias: spec.target_key
  for spec in DELIVERY_TARGET_SPECS
  for alias in spec.aliases
}

WORKFLOW_PROVIDER_SPEC_BY_KEY = {
  spec.provider_key: spec
  for spec in WORKFLOW_PROVIDER_SPECS
}


def normalize_delivery_target(target: str) -> str | None:
  normalized = target.strip().lower().replace("-", "_")
  if not normalized:
    return None
  return DELIVERY_TARGET_ALIAS_TO_KEY.get(normalized)


def normalize_workflow_provider(provider: str) -> str:
  return provider.strip().lower().replace("-", "_")


def list_enabled_workflow_providers(adapter: object) -> tuple[str, ...]:
  providers: list[str] = []
  for spec in WORKFLOW_PROVIDER_SPECS:
    if all(getattr(adapter, attr, None) for attr in spec.required_attrs):
      providers.append(spec.provider_key)
  return tuple(providers)


def resolve_delivery_handler(
  adapter: object,
  target: str,
) -> Callable[..., object] | None:
  spec = DELIVERY_TARGET_SPEC_BY_KEY.get(target)
  if spec is None:
    return None
  return getattr(adapter, spec.deliver_method_name, None)


def resolve_workflow_sync_handler(
  adapter: object,
  provider: str,
) -> Callable[..., object] | None:
  spec = WORKFLOW_PROVIDER_SPEC_BY_KEY.get(provider)
  if spec is None:
    return None
  return getattr(adapter, spec.sync_method_name, None)


def resolve_workflow_pull_handler(
  adapter: object,
  provider: str,
) -> Callable[..., object] | None:
  spec = WORKFLOW_PROVIDER_SPEC_BY_KEY.get(provider)
  if spec is None:
    return None
  return getattr(adapter, spec.pull_method_name, None)
