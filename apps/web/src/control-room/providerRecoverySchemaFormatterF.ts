import { formatTimestamp } from "./ControlRoomFormatBasics";
import type { ProviderRecoverySchemaInput } from "./providerRecoverySchemaTypes";

function formatProviderRecoverySchemaF(providerRecovery: ProviderRecoverySchemaInput) {
  if (providerRecovery.provider_schema_kind === "topdesk") {
    const details = [
      providerRecovery.topdesk.alert_id ? `alert ${providerRecovery.topdesk.alert_id}` : null,
      providerRecovery.topdesk.alert_status !== "unknown"
        ? `status ${providerRecovery.topdesk.alert_status}`
        : null,
      providerRecovery.topdesk.priority ? `priority ${providerRecovery.topdesk.priority}` : null,
      providerRecovery.topdesk.escalation_policy
        ? `policy ${providerRecovery.topdesk.escalation_policy}`
        : null,
      providerRecovery.topdesk.assignee ? `assignee ${providerRecovery.topdesk.assignee}` : null,
      providerRecovery.topdesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.topdesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.topdesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.topdesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.topdesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.topdesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `TOPdesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "invgateservicedesk") {
    const details = [
      providerRecovery.invgateservicedesk.alert_id
        ? `alert ${providerRecovery.invgateservicedesk.alert_id}`
        : null,
      providerRecovery.invgateservicedesk.alert_status !== "unknown"
        ? `status ${providerRecovery.invgateservicedesk.alert_status}`
        : null,
      providerRecovery.invgateservicedesk.priority
        ? `priority ${providerRecovery.invgateservicedesk.priority}`
        : null,
      providerRecovery.invgateservicedesk.escalation_policy
        ? `policy ${providerRecovery.invgateservicedesk.escalation_policy}`
        : null,
      providerRecovery.invgateservicedesk.assignee
        ? `assignee ${providerRecovery.invgateservicedesk.assignee}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.invgateservicedesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.invgateservicedesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.invgateservicedesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.invgateservicedesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.invgateservicedesk.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `InvGate Service Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "opsramp") {
    const details = [
      providerRecovery.opsramp.alert_id ? `alert ${providerRecovery.opsramp.alert_id}` : null,
      providerRecovery.opsramp.alert_status !== "unknown"
        ? `status ${providerRecovery.opsramp.alert_status}`
        : null,
      providerRecovery.opsramp.priority ? `priority ${providerRecovery.opsramp.priority}` : null,
      providerRecovery.opsramp.escalation_policy
        ? `policy ${providerRecovery.opsramp.escalation_policy}`
        : null,
      providerRecovery.opsramp.assignee ? `assignee ${providerRecovery.opsramp.assignee}` : null,
      providerRecovery.opsramp.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.opsramp.phase_graph.alert_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.opsramp.phase_graph.workflow_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.opsramp.phase_graph.ownership_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.opsramp.phase_graph.escalation_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.opsramp.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OpsRamp schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zenduty") {
    const details = [
      providerRecovery.zenduty.incident_id ? `incident ${providerRecovery.zenduty.incident_id}` : null,
      providerRecovery.zenduty.incident_status !== "unknown"
        ? `status ${providerRecovery.zenduty.incident_status}`
        : null,
      providerRecovery.zenduty.severity ? `severity ${providerRecovery.zenduty.severity}` : null,
      providerRecovery.zenduty.assignee ? `assignee ${providerRecovery.zenduty.assignee}` : null,
      providerRecovery.zenduty.service ? `service ${providerRecovery.zenduty.service}` : null,
      providerRecovery.zenduty.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.zenduty.phase_graph.incident_phase}`
        : null,
      providerRecovery.zenduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zenduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zenduty.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zenduty.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zenduty.updated_at
        ? `updated ${formatTimestamp(providerRecovery.zenduty.updated_at)}`
        : null,
      providerRecovery.zenduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zenduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zenduty schema: ${details.join(" / ")}` : null;
  }
  return null;
}

export { formatProviderRecoverySchemaF };
