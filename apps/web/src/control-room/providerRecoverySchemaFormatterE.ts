import { formatTimestamp } from "./ControlRoomFormatBasics";
import type { ProviderRecoverySchemaInput } from "./providerRecoverySchemaTypes";

function formatProviderRecoverySchemaE(providerRecovery: ProviderRecoverySchemaInput) {
  if (providerRecovery.provider_schema_kind === "zohodesk") {
    const details = [
      providerRecovery.zohodesk.alert_id
        ? `alert ${providerRecovery.zohodesk.alert_id}`
        : null,
      providerRecovery.zohodesk.alert_status !== "unknown"
        ? `status ${providerRecovery.zohodesk.alert_status}`
        : null,
      providerRecovery.zohodesk.priority
        ? `priority ${providerRecovery.zohodesk.priority}`
        : null,
      providerRecovery.zohodesk.escalation_policy
        ? `policy ${providerRecovery.zohodesk.escalation_policy}`
        : null,
      providerRecovery.zohodesk.assignee
        ? `assignee ${providerRecovery.zohodesk.assignee}`
        : null,
      providerRecovery.zohodesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.zohodesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zohodesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zohodesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.zohodesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zohodesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zoho Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "helpscout") {
    const details = [
      providerRecovery.helpscout.alert_id
        ? `alert ${providerRecovery.helpscout.alert_id}`
        : null,
      providerRecovery.helpscout.alert_status !== "unknown"
        ? `status ${providerRecovery.helpscout.alert_status}`
        : null,
      providerRecovery.helpscout.priority
        ? `priority ${providerRecovery.helpscout.priority}`
        : null,
      providerRecovery.helpscout.escalation_policy
        ? `policy ${providerRecovery.helpscout.escalation_policy}`
        : null,
      providerRecovery.helpscout.assignee
        ? `assignee ${providerRecovery.helpscout.assignee}`
        : null,
      providerRecovery.helpscout.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.helpscout.phase_graph.alert_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.helpscout.phase_graph.workflow_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.helpscout.phase_graph.ownership_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.helpscout.phase_graph.escalation_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.helpscout.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Help Scout schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "kayako") {
    const details = [
      providerRecovery.kayako.alert_id
        ? `case ${providerRecovery.kayako.alert_id}`
        : null,
      providerRecovery.kayako.alert_status !== "unknown"
        ? `status ${providerRecovery.kayako.alert_status}`
        : null,
      providerRecovery.kayako.priority
        ? `priority ${providerRecovery.kayako.priority}`
        : null,
      providerRecovery.kayako.escalation_policy
        ? `policy ${providerRecovery.kayako.escalation_policy}`
        : null,
      providerRecovery.kayako.assignee
        ? `assignee ${providerRecovery.kayako.assignee}`
        : null,
      providerRecovery.kayako.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.kayako.phase_graph.alert_phase}`
        : null,
      providerRecovery.kayako.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.kayako.phase_graph.workflow_phase}`
        : null,
      providerRecovery.kayako.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.kayako.phase_graph.ownership_phase}`
        : null,
      providerRecovery.kayako.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.kayako.phase_graph.escalation_phase}`
        : null,
      providerRecovery.kayako.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.kayako.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Kayako schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "intercom") {
    const details = [
      providerRecovery.intercom.alert_id
        ? `conversation ${providerRecovery.intercom.alert_id}`
        : null,
      providerRecovery.intercom.alert_status !== "unknown"
        ? `status ${providerRecovery.intercom.alert_status}`
        : null,
      providerRecovery.intercom.priority
        ? `priority ${providerRecovery.intercom.priority}`
        : null,
      providerRecovery.intercom.escalation_policy
        ? `policy ${providerRecovery.intercom.escalation_policy}`
        : null,
      providerRecovery.intercom.assignee
        ? `assignee ${providerRecovery.intercom.assignee}`
        : null,
      providerRecovery.intercom.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.intercom.phase_graph.alert_phase}`
        : null,
      providerRecovery.intercom.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.intercom.phase_graph.workflow_phase}`
        : null,
      providerRecovery.intercom.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.intercom.phase_graph.ownership_phase}`
        : null,
      providerRecovery.intercom.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.intercom.phase_graph.escalation_phase}`
        : null,
      providerRecovery.intercom.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.intercom.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Intercom schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "front") {
    const details = [
      providerRecovery.front.alert_id
        ? `conversation ${providerRecovery.front.alert_id}`
        : null,
      providerRecovery.front.alert_status !== "unknown"
        ? `status ${providerRecovery.front.alert_status}`
        : null,
      providerRecovery.front.priority
        ? `priority ${providerRecovery.front.priority}`
        : null,
      providerRecovery.front.escalation_policy
        ? `policy ${providerRecovery.front.escalation_policy}`
        : null,
      providerRecovery.front.assignee
        ? `assignee ${providerRecovery.front.assignee}`
        : null,
      providerRecovery.front.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.front.phase_graph.alert_phase}`
        : null,
      providerRecovery.front.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.front.phase_graph.workflow_phase}`
        : null,
      providerRecovery.front.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.front.phase_graph.ownership_phase}`
        : null,
      providerRecovery.front.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.front.phase_graph.escalation_phase}`
        : null,
      providerRecovery.front.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.front.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Front schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "servicedeskplus") {
    const details = [
      providerRecovery.servicedeskplus.alert_id
        ? `alert ${providerRecovery.servicedeskplus.alert_id}`
        : null,
      providerRecovery.servicedeskplus.alert_status !== "unknown"
        ? `status ${providerRecovery.servicedeskplus.alert_status}`
        : null,
      providerRecovery.servicedeskplus.priority
        ? `priority ${providerRecovery.servicedeskplus.priority}`
        : null,
      providerRecovery.servicedeskplus.escalation_policy
        ? `policy ${providerRecovery.servicedeskplus.escalation_policy}`
        : null,
      providerRecovery.servicedeskplus.assignee
        ? `assignee ${providerRecovery.servicedeskplus.assignee}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.servicedeskplus.phase_graph.alert_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.servicedeskplus.phase_graph.workflow_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.servicedeskplus.phase_graph.ownership_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.servicedeskplus.phase_graph.escalation_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.servicedeskplus.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `ManageEngine ServiceDesk Plus schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "sysaid") {
    const details = [
      providerRecovery.sysaid.alert_id ? `alert ${providerRecovery.sysaid.alert_id}` : null,
      providerRecovery.sysaid.alert_status !== "unknown"
        ? `status ${providerRecovery.sysaid.alert_status}`
        : null,
      providerRecovery.sysaid.priority ? `priority ${providerRecovery.sysaid.priority}` : null,
      providerRecovery.sysaid.escalation_policy
        ? `policy ${providerRecovery.sysaid.escalation_policy}`
        : null,
      providerRecovery.sysaid.assignee ? `assignee ${providerRecovery.sysaid.assignee}` : null,
      providerRecovery.sysaid.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.sysaid.phase_graph.alert_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.sysaid.phase_graph.workflow_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.sysaid.phase_graph.ownership_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.sysaid.phase_graph.escalation_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.sysaid.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `SysAid schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "bmchelix") {
    const details = [
      providerRecovery.bmchelix.alert_id ? `alert ${providerRecovery.bmchelix.alert_id}` : null,
      providerRecovery.bmchelix.alert_status !== "unknown"
        ? `status ${providerRecovery.bmchelix.alert_status}`
        : null,
      providerRecovery.bmchelix.priority ? `priority ${providerRecovery.bmchelix.priority}` : null,
      providerRecovery.bmchelix.escalation_policy
        ? `policy ${providerRecovery.bmchelix.escalation_policy}`
        : null,
      providerRecovery.bmchelix.assignee ? `assignee ${providerRecovery.bmchelix.assignee}` : null,
      providerRecovery.bmchelix.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.bmchelix.phase_graph.alert_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.bmchelix.phase_graph.workflow_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.bmchelix.phase_graph.ownership_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.bmchelix.phase_graph.escalation_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.bmchelix.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `BMC Helix schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "solarwindsservicedesk") {
    const details = [
      providerRecovery.solarwindsservicedesk.alert_id
        ? `alert ${providerRecovery.solarwindsservicedesk.alert_id}`
        : null,
      providerRecovery.solarwindsservicedesk.alert_status !== "unknown"
        ? `status ${providerRecovery.solarwindsservicedesk.alert_status}`
        : null,
      providerRecovery.solarwindsservicedesk.priority
        ? `priority ${providerRecovery.solarwindsservicedesk.priority}`
        : null,
      providerRecovery.solarwindsservicedesk.escalation_policy
        ? `policy ${providerRecovery.solarwindsservicedesk.escalation_policy}`
        : null,
      providerRecovery.solarwindsservicedesk.assignee
        ? `assignee ${providerRecovery.solarwindsservicedesk.assignee}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.solarwindsservicedesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.solarwindsservicedesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.solarwindsservicedesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.solarwindsservicedesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.solarwindsservicedesk.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `SolarWinds Service Desk schema: ${details.join(" / ")}` : null;
  }
  return null;
}

export { formatProviderRecoverySchemaE };
