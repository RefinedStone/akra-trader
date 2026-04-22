from __future__ import annotations

from urllib import request as urllib_request


class OperatorDeliveryRecoveryEngineRequestMixin:
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

  def _build_crisescontrol_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._crisescontrol_recovery_engine_token or self._crisescontrol_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_freshservice_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._freshservice_recovery_engine_token or self._freshservice_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_freshdesk_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._freshdesk_recovery_engine_token or self._freshdesk_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_happyfox_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._happyfox_recovery_engine_token or self._happyfox_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_helpscout_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._helpscout_recovery_engine_token or self._helpscout_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_kayako_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._kayako_recovery_engine_token or self._kayako_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_intercom_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._intercom_recovery_engine_token or self._intercom_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_front_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._front_recovery_engine_token or self._front_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_zendesk_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._zendesk_recovery_engine_token or self._zendesk_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_zohodesk_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._zohodesk_recovery_engine_token or self._zohodesk_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_servicedeskplus_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._servicedeskplus_recovery_engine_token or self._servicedeskplus_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_sysaid_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._sysaid_recovery_engine_token or self._sysaid_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_bmchelix_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._bmchelix_recovery_engine_token or self._bmchelix_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_solarwindsservicedesk_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = (
      self._solarwindsservicedesk_recovery_engine_token
      or self._solarwindsservicedesk_api_token
    )
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_topdesk_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._topdesk_recovery_engine_token or self._topdesk_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_invgateservicedesk_recovery_engine_request(
    self,
    *,
    url: str,
  ) -> urllib_request.Request:
    token = self._invgateservicedesk_recovery_engine_token or self._invgateservicedesk_api_token
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
