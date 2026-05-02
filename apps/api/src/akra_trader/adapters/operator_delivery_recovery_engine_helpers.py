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


class OperatorDeliveryRecoveryEngineHelpersMixin:
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
  @classmethod
  def _format_recovery_engine_url(
    cls,
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
    context = cls._build_recovery_engine_template_context(
      workflow_reference=workflow_reference,
      external_reference=external_reference,
      job_id=job_id,
    )
    try:
      return url_template.format_map(context)
    except KeyError:
      return None
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
    elif provider == "crisescontrol":
      url = self._format_recovery_engine_url(
        url_template=self._crisescontrol_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_crisescontrol_recovery_engine_request(url=url)
    elif provider == "freshservice":
      url = self._format_recovery_engine_url(
        url_template=self._freshservice_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_freshservice_recovery_engine_request(url=url)
    elif provider == "freshdesk":
      url = self._format_recovery_engine_url(
        url_template=self._freshdesk_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_freshdesk_recovery_engine_request(url=url)
    elif provider == "happyfox":
      url = self._format_recovery_engine_url(
        url_template=self._happyfox_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_happyfox_recovery_engine_request(url=url)
    elif provider == "zendesk":
      url = self._format_recovery_engine_url(
        url_template=self._zendesk_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_zendesk_recovery_engine_request(url=url)
    elif provider == "zohodesk":
      url = self._format_recovery_engine_url(
        url_template=self._zohodesk_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_zohodesk_recovery_engine_request(url=url)
    elif provider == "helpscout":
      url = self._format_recovery_engine_url(
        url_template=self._helpscout_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_helpscout_recovery_engine_request(url=url)
    elif provider == "kayako":
      url = self._format_recovery_engine_url(
        url_template=self._kayako_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_kayako_recovery_engine_request(url=url)
    elif provider == "intercom":
      url = self._format_recovery_engine_url(
        url_template=self._intercom_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_intercom_recovery_engine_request(url=url)
    elif provider == "front":
      url = self._format_recovery_engine_url(
        url_template=self._front_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_front_recovery_engine_request(url=url)
    elif provider == "servicedeskplus":
      url = self._format_recovery_engine_url(
        url_template=self._servicedeskplus_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_servicedeskplus_recovery_engine_request(url=url)
    elif provider == "sysaid":
      url = self._format_recovery_engine_url(
        url_template=self._sysaid_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_sysaid_recovery_engine_request(url=url)
    elif provider == "bmchelix":
      url = self._format_recovery_engine_url(
        url_template=self._bmchelix_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_bmchelix_recovery_engine_request(url=url)
    elif provider == "solarwindsservicedesk":
      url = self._format_recovery_engine_url(
        url_template=self._solarwindsservicedesk_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_solarwindsservicedesk_recovery_engine_request(url=url)
    elif provider == "topdesk":
      url = self._format_recovery_engine_url(
        url_template=self._topdesk_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_topdesk_recovery_engine_request(url=url)
    elif provider == "invgateservicedesk":
      url = self._format_recovery_engine_url(
        url_template=self._invgateservicedesk_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_invgateservicedesk_recovery_engine_request(url=url)
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
