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
from akra_trader.adapters.operator_delivery_provider_pull_schema import OperatorDeliveryProviderPullSchemaMixin


LOGGER = logging.getLogger("akra_trader.operator_delivery")


from akra_trader.adapters.operator_delivery_provider_recovery_payload_group_one import OperatorDeliveryProviderRecoveryPayloadGroupOneMixin
from akra_trader.adapters.operator_delivery_provider_recovery_payload_group_two import OperatorDeliveryProviderRecoveryPayloadGroupTwoMixin


class OperatorDeliveryProviderRecoveryPayloadMixin(
  OperatorDeliveryProviderRecoveryPayloadGroupOneMixin,
  OperatorDeliveryProviderRecoveryPayloadGroupTwoMixin,
):
  @staticmethod
  def _build_provider_recovery_payload_schema(provider_recovery: Any) -> dict[str, Any]:
    return {
      **OperatorDeliveryProviderRecoveryPayloadGroupOneMixin._build_provider_recovery_payload_schema_group_one(provider_recovery),
      **OperatorDeliveryProviderRecoveryPayloadGroupTwoMixin._build_provider_recovery_payload_schema_group_two(provider_recovery),
    }
