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


class OperatorDeliveryProviderRecoveryPayloadGroupTwoMixin:
  @staticmethod
  def _build_provider_recovery_payload_schema_group_two(provider_recovery: Any) -> dict[str, Any]:
    return {
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
      "crisescontrol": {
        "alert_id": provider_recovery.crisescontrol.alert_id,
        "external_reference": provider_recovery.crisescontrol.external_reference,
        "alert_status": provider_recovery.crisescontrol.alert_status,
        "priority": provider_recovery.crisescontrol.priority,
        "escalation_policy": provider_recovery.crisescontrol.escalation_policy,
        "assignee": provider_recovery.crisescontrol.assignee,
        "url": provider_recovery.crisescontrol.url,
        "updated_at": (
          provider_recovery.crisescontrol.updated_at.isoformat()
          if provider_recovery.crisescontrol.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.crisescontrol.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.crisescontrol.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.crisescontrol.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.crisescontrol.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.crisescontrol.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.crisescontrol.phase_graph.last_transition_at.isoformat()
            if provider_recovery.crisescontrol.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "freshservice": {
        "alert_id": provider_recovery.freshservice.alert_id,
        "external_reference": provider_recovery.freshservice.external_reference,
        "alert_status": provider_recovery.freshservice.alert_status,
        "priority": provider_recovery.freshservice.priority,
        "escalation_policy": provider_recovery.freshservice.escalation_policy,
        "assignee": provider_recovery.freshservice.assignee,
        "url": provider_recovery.freshservice.url,
        "updated_at": (
          provider_recovery.freshservice.updated_at.isoformat()
          if provider_recovery.freshservice.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.freshservice.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.freshservice.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.freshservice.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.freshservice.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.freshservice.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.freshservice.phase_graph.last_transition_at.isoformat()
            if provider_recovery.freshservice.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "freshdesk": {
        "alert_id": provider_recovery.freshdesk.alert_id,
        "external_reference": provider_recovery.freshdesk.external_reference,
        "alert_status": provider_recovery.freshdesk.alert_status,
        "priority": provider_recovery.freshdesk.priority,
        "escalation_policy": provider_recovery.freshdesk.escalation_policy,
        "assignee": provider_recovery.freshdesk.assignee,
        "url": provider_recovery.freshdesk.url,
        "updated_at": (
          provider_recovery.freshdesk.updated_at.isoformat()
          if provider_recovery.freshdesk.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.freshdesk.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.freshdesk.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.freshdesk.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.freshdesk.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.freshdesk.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.freshdesk.phase_graph.last_transition_at.isoformat()
            if provider_recovery.freshdesk.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "happyfox": {
        "alert_id": provider_recovery.happyfox.alert_id,
        "external_reference": provider_recovery.happyfox.external_reference,
        "alert_status": provider_recovery.happyfox.alert_status,
        "priority": provider_recovery.happyfox.priority,
        "escalation_policy": provider_recovery.happyfox.escalation_policy,
        "assignee": provider_recovery.happyfox.assignee,
        "url": provider_recovery.happyfox.url,
        "updated_at": (
          provider_recovery.happyfox.updated_at.isoformat()
          if provider_recovery.happyfox.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.happyfox.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.happyfox.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.happyfox.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.happyfox.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.happyfox.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.happyfox.phase_graph.last_transition_at.isoformat()
            if provider_recovery.happyfox.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "zendesk": {
        "alert_id": provider_recovery.zendesk.alert_id,
        "external_reference": provider_recovery.zendesk.external_reference,
        "alert_status": provider_recovery.zendesk.alert_status,
        "priority": provider_recovery.zendesk.priority,
        "escalation_policy": provider_recovery.zendesk.escalation_policy,
        "assignee": provider_recovery.zendesk.assignee,
        "url": provider_recovery.zendesk.url,
        "updated_at": (
          provider_recovery.zendesk.updated_at.isoformat()
          if provider_recovery.zendesk.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.zendesk.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.zendesk.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.zendesk.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.zendesk.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.zendesk.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.zendesk.phase_graph.last_transition_at.isoformat()
            if provider_recovery.zendesk.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "zohodesk": {
        "alert_id": provider_recovery.zohodesk.alert_id,
        "external_reference": provider_recovery.zohodesk.external_reference,
        "alert_status": provider_recovery.zohodesk.alert_status,
        "priority": provider_recovery.zohodesk.priority,
        "escalation_policy": provider_recovery.zohodesk.escalation_policy,
        "assignee": provider_recovery.zohodesk.assignee,
        "url": provider_recovery.zohodesk.url,
        "updated_at": (
          provider_recovery.zohodesk.updated_at.isoformat()
          if provider_recovery.zohodesk.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.zohodesk.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.zohodesk.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.zohodesk.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.zohodesk.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.zohodesk.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.zohodesk.phase_graph.last_transition_at.isoformat()
            if provider_recovery.zohodesk.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "helpscout": {
        "alert_id": provider_recovery.helpscout.alert_id,
        "external_reference": provider_recovery.helpscout.external_reference,
        "alert_status": provider_recovery.helpscout.alert_status,
        "priority": provider_recovery.helpscout.priority,
        "escalation_policy": provider_recovery.helpscout.escalation_policy,
        "assignee": provider_recovery.helpscout.assignee,
        "url": provider_recovery.helpscout.url,
        "updated_at": (
          provider_recovery.helpscout.updated_at.isoformat()
          if provider_recovery.helpscout.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.helpscout.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.helpscout.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.helpscout.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.helpscout.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.helpscout.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.helpscout.phase_graph.last_transition_at.isoformat()
            if provider_recovery.helpscout.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "kayako": {
        "alert_id": provider_recovery.kayako.alert_id,
        "external_reference": provider_recovery.kayako.external_reference,
        "alert_status": provider_recovery.kayako.alert_status,
        "priority": provider_recovery.kayako.priority,
        "escalation_policy": provider_recovery.kayako.escalation_policy,
        "assignee": provider_recovery.kayako.assignee,
        "url": provider_recovery.kayako.url,
        "updated_at": (
          provider_recovery.kayako.updated_at.isoformat()
          if provider_recovery.kayako.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.kayako.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.kayako.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.kayako.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.kayako.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.kayako.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.kayako.phase_graph.last_transition_at.isoformat()
            if provider_recovery.kayako.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "intercom": {
        "alert_id": provider_recovery.intercom.alert_id,
        "external_reference": provider_recovery.intercom.external_reference,
        "alert_status": provider_recovery.intercom.alert_status,
        "priority": provider_recovery.intercom.priority,
        "escalation_policy": provider_recovery.intercom.escalation_policy,
        "assignee": provider_recovery.intercom.assignee,
        "url": provider_recovery.intercom.url,
        "updated_at": (
          provider_recovery.intercom.updated_at.isoformat()
          if provider_recovery.intercom.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.intercom.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.intercom.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.intercom.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.intercom.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.intercom.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.intercom.phase_graph.last_transition_at.isoformat()
            if provider_recovery.intercom.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "front": {
        "alert_id": provider_recovery.front.alert_id,
        "external_reference": provider_recovery.front.external_reference,
        "alert_status": provider_recovery.front.alert_status,
        "priority": provider_recovery.front.priority,
        "escalation_policy": provider_recovery.front.escalation_policy,
        "assignee": provider_recovery.front.assignee,
        "url": provider_recovery.front.url,
        "updated_at": (
          provider_recovery.front.updated_at.isoformat()
          if provider_recovery.front.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.front.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.front.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.front.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.front.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.front.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.front.phase_graph.last_transition_at.isoformat()
            if provider_recovery.front.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "servicedeskplus": {
        "alert_id": provider_recovery.servicedeskplus.alert_id,
        "external_reference": provider_recovery.servicedeskplus.external_reference,
        "alert_status": provider_recovery.servicedeskplus.alert_status,
        "priority": provider_recovery.servicedeskplus.priority,
        "escalation_policy": provider_recovery.servicedeskplus.escalation_policy,
        "assignee": provider_recovery.servicedeskplus.assignee,
        "url": provider_recovery.servicedeskplus.url,
        "updated_at": (
          provider_recovery.servicedeskplus.updated_at.isoformat()
          if provider_recovery.servicedeskplus.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.servicedeskplus.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.servicedeskplus.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.servicedeskplus.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.servicedeskplus.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.servicedeskplus.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.servicedeskplus.phase_graph.last_transition_at.isoformat()
            if provider_recovery.servicedeskplus.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "sysaid": {
        "alert_id": provider_recovery.sysaid.alert_id,
        "external_reference": provider_recovery.sysaid.external_reference,
        "alert_status": provider_recovery.sysaid.alert_status,
        "priority": provider_recovery.sysaid.priority,
        "escalation_policy": provider_recovery.sysaid.escalation_policy,
        "assignee": provider_recovery.sysaid.assignee,
        "url": provider_recovery.sysaid.url,
        "updated_at": (
          provider_recovery.sysaid.updated_at.isoformat()
          if provider_recovery.sysaid.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.sysaid.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.sysaid.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.sysaid.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.sysaid.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.sysaid.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.sysaid.phase_graph.last_transition_at.isoformat()
            if provider_recovery.sysaid.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "bmchelix": {
        "alert_id": provider_recovery.bmchelix.alert_id,
        "external_reference": provider_recovery.bmchelix.external_reference,
        "alert_status": provider_recovery.bmchelix.alert_status,
        "priority": provider_recovery.bmchelix.priority,
        "escalation_policy": provider_recovery.bmchelix.escalation_policy,
        "assignee": provider_recovery.bmchelix.assignee,
        "url": provider_recovery.bmchelix.url,
        "updated_at": (
          provider_recovery.bmchelix.updated_at.isoformat()
          if provider_recovery.bmchelix.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.bmchelix.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.bmchelix.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.bmchelix.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.bmchelix.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.bmchelix.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.bmchelix.phase_graph.last_transition_at.isoformat()
            if provider_recovery.bmchelix.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "solarwindsservicedesk": {
        "alert_id": provider_recovery.solarwindsservicedesk.alert_id,
        "external_reference": provider_recovery.solarwindsservicedesk.external_reference,
        "alert_status": provider_recovery.solarwindsservicedesk.alert_status,
        "priority": provider_recovery.solarwindsservicedesk.priority,
        "escalation_policy": provider_recovery.solarwindsservicedesk.escalation_policy,
        "assignee": provider_recovery.solarwindsservicedesk.assignee,
        "url": provider_recovery.solarwindsservicedesk.url,
        "updated_at": (
          provider_recovery.solarwindsservicedesk.updated_at.isoformat()
          if provider_recovery.solarwindsservicedesk.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.solarwindsservicedesk.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.solarwindsservicedesk.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.solarwindsservicedesk.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.solarwindsservicedesk.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.solarwindsservicedesk.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.solarwindsservicedesk.phase_graph.last_transition_at.isoformat()
            if provider_recovery.solarwindsservicedesk.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "topdesk": {
        "alert_id": provider_recovery.topdesk.alert_id,
        "external_reference": provider_recovery.topdesk.external_reference,
        "alert_status": provider_recovery.topdesk.alert_status,
        "priority": provider_recovery.topdesk.priority,
        "escalation_policy": provider_recovery.topdesk.escalation_policy,
        "assignee": provider_recovery.topdesk.assignee,
        "url": provider_recovery.topdesk.url,
        "updated_at": (
          provider_recovery.topdesk.updated_at.isoformat()
          if provider_recovery.topdesk.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.topdesk.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.topdesk.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.topdesk.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.topdesk.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.topdesk.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.topdesk.phase_graph.last_transition_at.isoformat()
            if provider_recovery.topdesk.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "invgateservicedesk": {
        "alert_id": provider_recovery.invgateservicedesk.alert_id,
        "external_reference": provider_recovery.invgateservicedesk.external_reference,
        "alert_status": provider_recovery.invgateservicedesk.alert_status,
        "priority": provider_recovery.invgateservicedesk.priority,
        "escalation_policy": provider_recovery.invgateservicedesk.escalation_policy,
        "assignee": provider_recovery.invgateservicedesk.assignee,
        "url": provider_recovery.invgateservicedesk.url,
        "updated_at": (
          provider_recovery.invgateservicedesk.updated_at.isoformat()
          if provider_recovery.invgateservicedesk.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.invgateservicedesk.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.invgateservicedesk.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.invgateservicedesk.phase_graph.ownership_phase,
          "priority_phase": provider_recovery.invgateservicedesk.phase_graph.priority_phase,
          "escalation_phase": provider_recovery.invgateservicedesk.phase_graph.escalation_phase,
          "last_transition_at": (
            provider_recovery.invgateservicedesk.phase_graph.last_transition_at.isoformat()
            if provider_recovery.invgateservicedesk.phase_graph.last_transition_at is not None
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
