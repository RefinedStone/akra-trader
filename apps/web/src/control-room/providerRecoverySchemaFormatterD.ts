import { formatTimestamp } from "./ControlRoomFormatBasics";
import type { ProviderRecoverySchemaInput } from "./providerRecoverySchemaTypes";

function formatProviderRecoverySchemaD(providerRecovery: ProviderRecoverySchemaInput) {
  if (providerRecovery.provider_schema_kind === "haloitsm") {
    const details = [
      providerRecovery.haloitsm.alert_id ? `alert ${providerRecovery.haloitsm.alert_id}` : null,
      providerRecovery.haloitsm.alert_status !== "unknown"
        ? `status ${providerRecovery.haloitsm.alert_status}`
        : null,
      providerRecovery.haloitsm.priority ? `priority ${providerRecovery.haloitsm.priority}` : null,
      providerRecovery.haloitsm.escalation_policy
        ? `policy ${providerRecovery.haloitsm.escalation_policy}`
        : null,
      providerRecovery.haloitsm.assignee ? `assignee ${providerRecovery.haloitsm.assignee}` : null,
      providerRecovery.haloitsm.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.haloitsm.phase_graph.alert_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.haloitsm.phase_graph.workflow_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.haloitsm.phase_graph.ownership_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.haloitsm.phase_graph.escalation_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.haloitsm.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `HaloITSM schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidentmanagerio") {
    const details = [
      providerRecovery.incidentmanagerio.alert_id
        ? `alert ${providerRecovery.incidentmanagerio.alert_id}`
        : null,
      providerRecovery.incidentmanagerio.alert_status !== "unknown"
        ? `status ${providerRecovery.incidentmanagerio.alert_status}`
        : null,
      providerRecovery.incidentmanagerio.priority
        ? `priority ${providerRecovery.incidentmanagerio.priority}`
        : null,
      providerRecovery.incidentmanagerio.escalation_policy
        ? `policy ${providerRecovery.incidentmanagerio.escalation_policy}`
        : null,
      providerRecovery.incidentmanagerio.assignee
        ? `assignee ${providerRecovery.incidentmanagerio.assignee}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.incidentmanagerio.phase_graph.alert_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidentmanagerio.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.incidentmanagerio.phase_graph.ownership_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.incidentmanagerio.phase_graph.escalation_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidentmanagerio.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `incidentmanager.io schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "oneuptime") {
    const details = [
      providerRecovery.oneuptime.alert_id ? `alert ${providerRecovery.oneuptime.alert_id}` : null,
      providerRecovery.oneuptime.alert_status !== "unknown"
        ? `status ${providerRecovery.oneuptime.alert_status}`
        : null,
      providerRecovery.oneuptime.priority ? `priority ${providerRecovery.oneuptime.priority}` : null,
      providerRecovery.oneuptime.escalation_policy
        ? `policy ${providerRecovery.oneuptime.escalation_policy}`
        : null,
      providerRecovery.oneuptime.assignee ? `assignee ${providerRecovery.oneuptime.assignee}` : null,
      providerRecovery.oneuptime.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.oneuptime.phase_graph.alert_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.oneuptime.phase_graph.workflow_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.oneuptime.phase_graph.ownership_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.oneuptime.phase_graph.escalation_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.oneuptime.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OneUptime schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "squzy") {
    const details = [
      providerRecovery.squzy.alert_id ? `alert ${providerRecovery.squzy.alert_id}` : null,
      providerRecovery.squzy.alert_status !== "unknown"
        ? `status ${providerRecovery.squzy.alert_status}`
        : null,
      providerRecovery.squzy.priority ? `priority ${providerRecovery.squzy.priority}` : null,
      providerRecovery.squzy.escalation_policy
        ? `policy ${providerRecovery.squzy.escalation_policy}`
        : null,
      providerRecovery.squzy.assignee ? `assignee ${providerRecovery.squzy.assignee}` : null,
      providerRecovery.squzy.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.squzy.phase_graph.alert_phase}`
        : null,
      providerRecovery.squzy.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.squzy.phase_graph.workflow_phase}`
        : null,
      providerRecovery.squzy.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.squzy.phase_graph.ownership_phase}`
        : null,
      providerRecovery.squzy.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.squzy.phase_graph.escalation_phase}`
        : null,
      providerRecovery.squzy.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.squzy.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Squzy schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "crisescontrol") {
    const details = [
      providerRecovery.crisescontrol.alert_id
        ? `alert ${providerRecovery.crisescontrol.alert_id}`
        : null,
      providerRecovery.crisescontrol.alert_status !== "unknown"
        ? `status ${providerRecovery.crisescontrol.alert_status}`
        : null,
      providerRecovery.crisescontrol.priority
        ? `priority ${providerRecovery.crisescontrol.priority}`
        : null,
      providerRecovery.crisescontrol.escalation_policy
        ? `policy ${providerRecovery.crisescontrol.escalation_policy}`
        : null,
      providerRecovery.crisescontrol.assignee
        ? `assignee ${providerRecovery.crisescontrol.assignee}`
        : null,
      providerRecovery.crisescontrol.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.crisescontrol.phase_graph.alert_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.crisescontrol.phase_graph.workflow_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.crisescontrol.phase_graph.ownership_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.crisescontrol.phase_graph.escalation_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.crisescontrol.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Crises Control schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "freshservice") {
    const details = [
      providerRecovery.freshservice.alert_id
        ? `alert ${providerRecovery.freshservice.alert_id}`
        : null,
      providerRecovery.freshservice.alert_status !== "unknown"
        ? `status ${providerRecovery.freshservice.alert_status}`
        : null,
      providerRecovery.freshservice.priority
        ? `priority ${providerRecovery.freshservice.priority}`
        : null,
      providerRecovery.freshservice.escalation_policy
        ? `policy ${providerRecovery.freshservice.escalation_policy}`
        : null,
      providerRecovery.freshservice.assignee
        ? `assignee ${providerRecovery.freshservice.assignee}`
        : null,
      providerRecovery.freshservice.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.freshservice.phase_graph.alert_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.freshservice.phase_graph.workflow_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.freshservice.phase_graph.ownership_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.freshservice.phase_graph.escalation_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.freshservice.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Freshservice schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "freshdesk") {
    const details = [
      providerRecovery.freshdesk.alert_id
        ? `alert ${providerRecovery.freshdesk.alert_id}`
        : null,
      providerRecovery.freshdesk.alert_status !== "unknown"
        ? `status ${providerRecovery.freshdesk.alert_status}`
        : null,
      providerRecovery.freshdesk.priority
        ? `priority ${providerRecovery.freshdesk.priority}`
        : null,
      providerRecovery.freshdesk.escalation_policy
        ? `policy ${providerRecovery.freshdesk.escalation_policy}`
        : null,
      providerRecovery.freshdesk.assignee
        ? `assignee ${providerRecovery.freshdesk.assignee}`
        : null,
      providerRecovery.freshdesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.freshdesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.freshdesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.freshdesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.freshdesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.freshdesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Freshdesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "happyfox") {
    const details = [
      providerRecovery.happyfox.alert_id
        ? `alert ${providerRecovery.happyfox.alert_id}`
        : null,
      providerRecovery.happyfox.alert_status !== "unknown"
        ? `status ${providerRecovery.happyfox.alert_status}`
        : null,
      providerRecovery.happyfox.priority
        ? `priority ${providerRecovery.happyfox.priority}`
        : null,
      providerRecovery.happyfox.escalation_policy
        ? `policy ${providerRecovery.happyfox.escalation_policy}`
        : null,
      providerRecovery.happyfox.assignee
        ? `assignee ${providerRecovery.happyfox.assignee}`
        : null,
      providerRecovery.happyfox.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.happyfox.phase_graph.alert_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.happyfox.phase_graph.workflow_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.happyfox.phase_graph.ownership_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.happyfox.phase_graph.escalation_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.happyfox.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `HappyFox schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zendesk") {
    const details = [
      providerRecovery.zendesk.alert_id
        ? `alert ${providerRecovery.zendesk.alert_id}`
        : null,
      providerRecovery.zendesk.alert_status !== "unknown"
        ? `status ${providerRecovery.zendesk.alert_status}`
        : null,
      providerRecovery.zendesk.priority
        ? `priority ${providerRecovery.zendesk.priority}`
        : null,
      providerRecovery.zendesk.escalation_policy
        ? `policy ${providerRecovery.zendesk.escalation_policy}`
        : null,
      providerRecovery.zendesk.assignee
        ? `assignee ${providerRecovery.zendesk.assignee}`
        : null,
      providerRecovery.zendesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.zendesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zendesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zendesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.zendesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zendesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zendesk schema: ${details.join(" / ")}` : null;
  }
  return null;
}

export { formatProviderRecoverySchemaD };
