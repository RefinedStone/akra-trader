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


from akra_trader.adapters.operator_delivery_provider_pull_schema_group_one import OperatorDeliveryProviderPullSchemaGroupOneMixin
from akra_trader.adapters.operator_delivery_provider_pull_schema_group_two import OperatorDeliveryProviderPullSchemaGroupTwoMixin
from akra_trader.adapters.operator_delivery_provider_pull_schema_group_three import OperatorDeliveryProviderPullSchemaGroupThreeMixin
from akra_trader.adapters.operator_delivery_provider_pull_schema_group_four import OperatorDeliveryProviderPullSchemaGroupFourMixin
from akra_trader.adapters.operator_delivery_provider_pull_schema_group_five import OperatorDeliveryProviderPullSchemaGroupFiveMixin
from akra_trader.adapters.operator_delivery_provider_pull_schema_group_six import OperatorDeliveryProviderPullSchemaGroupSixMixin
from akra_trader.adapters.operator_delivery_provider_pull_schema_group_seven import OperatorDeliveryProviderPullSchemaGroupSevenMixin


class OperatorDeliveryProviderPullSchemaMixin(
  OperatorDeliveryProviderPullSchemaGroupOneMixin,
  OperatorDeliveryProviderPullSchemaGroupTwoMixin,
  OperatorDeliveryProviderPullSchemaGroupThreeMixin,
  OperatorDeliveryProviderPullSchemaGroupFourMixin,
  OperatorDeliveryProviderPullSchemaGroupFiveMixin,
  OperatorDeliveryProviderPullSchemaGroupSixMixin,
  OperatorDeliveryProviderPullSchemaGroupSevenMixin,
):
  def _build_provider_pull_sync_schema_payload(
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
    for build_payload in (
      self._build_provider_pull_sync_schema_payload_group_one,
      self._build_provider_pull_sync_schema_payload_group_two,
      self._build_provider_pull_sync_schema_payload_group_three,
      self._build_provider_pull_sync_schema_payload_group_four,
      self._build_provider_pull_sync_schema_payload_group_five,
      self._build_provider_pull_sync_schema_payload_group_six,
      self._build_provider_pull_sync_schema_payload_group_seven,
    ):
      payload = build_payload(
        provider=provider,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        workflow_state=workflow_state,
        detail=detail,
        provider_payload=provider_payload,
        remediation_payload=remediation_payload,
        provider_recovery=provider_recovery,
        provider_telemetry=provider_telemetry,
        market_context=market_context,
        provider_specific_recovery=provider_specific_recovery,
        status_machine_payload=status_machine_payload,
        engine_telemetry=engine_telemetry,
        job_id=job_id,
        updated_at=updated_at,
      )
      if payload is not None:
        return payload
    return None
