import { formatTimestamp } from "./ControlRoomFormatBasics";
import type { ProviderRecoverySchemaInput } from "./providerRecoverySchemaTypes";

function formatProviderRecoverySchemaA(providerRecovery: ProviderRecoverySchemaInput) {
  if (providerRecovery.provider_schema_kind === "pagerduty") {
    const details = [
      providerRecovery.pagerduty.incident_id ? `incident ${providerRecovery.pagerduty.incident_id}` : null,
      providerRecovery.pagerduty.incident_status !== "unknown"
        ? `status ${providerRecovery.pagerduty.incident_status}`
        : null,
      providerRecovery.pagerduty.urgency ? `urgency ${providerRecovery.pagerduty.urgency}` : null,
      providerRecovery.pagerduty.service_summary ? `service ${providerRecovery.pagerduty.service_summary}` : null,
      providerRecovery.pagerduty.escalation_policy_summary
        ? `policy ${providerRecovery.pagerduty.escalation_policy_summary}`
        : null,
      providerRecovery.pagerduty.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.pagerduty.phase_graph.incident_phase}`
        : null,
      providerRecovery.pagerduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.pagerduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.pagerduty.phase_graph.responder_phase !== "unknown"
        ? `responder ${providerRecovery.pagerduty.phase_graph.responder_phase}`
        : null,
      providerRecovery.pagerduty.last_status_change_at
        ? `changed ${formatTimestamp(providerRecovery.pagerduty.last_status_change_at)}`
        : null,
      providerRecovery.pagerduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.pagerduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `PagerDuty schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "opsgenie") {
    const details = [
      providerRecovery.opsgenie.alert_id ? `alert ${providerRecovery.opsgenie.alert_id}` : null,
      providerRecovery.opsgenie.alert_status !== "unknown"
        ? `status ${providerRecovery.opsgenie.alert_status}`
        : null,
      providerRecovery.opsgenie.priority ? `priority ${providerRecovery.opsgenie.priority}` : null,
      providerRecovery.opsgenie.owner ? `owner ${providerRecovery.opsgenie.owner}` : null,
      providerRecovery.opsgenie.teams.length
        ? `teams ${providerRecovery.opsgenie.teams.join(", ")}`
        : null,
      providerRecovery.opsgenie.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.opsgenie.phase_graph.alert_phase}`
        : null,
      providerRecovery.opsgenie.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.opsgenie.phase_graph.workflow_phase}`
        : null,
      providerRecovery.opsgenie.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.opsgenie.phase_graph.ownership_phase}`
        : null,
      providerRecovery.opsgenie.updated_at
        ? `updated ${formatTimestamp(providerRecovery.opsgenie.updated_at)}`
        : null,
      providerRecovery.opsgenie.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.opsgenie.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Opsgenie schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidentio") {
    const details = [
      providerRecovery.incidentio.incident_id ? `incident ${providerRecovery.incidentio.incident_id}` : null,
      providerRecovery.incidentio.incident_status !== "unknown"
        ? `status ${providerRecovery.incidentio.incident_status}`
        : null,
      providerRecovery.incidentio.severity ? `severity ${providerRecovery.incidentio.severity}` : null,
      providerRecovery.incidentio.assignee ? `assignee ${providerRecovery.incidentio.assignee}` : null,
      providerRecovery.incidentio.visibility ? `visibility ${providerRecovery.incidentio.visibility}` : null,
      providerRecovery.incidentio.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.incidentio.phase_graph.incident_phase}`
        : null,
      providerRecovery.incidentio.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidentio.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidentio.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.incidentio.phase_graph.assignment_phase}`
        : null,
      providerRecovery.incidentio.updated_at
        ? `updated ${formatTimestamp(providerRecovery.incidentio.updated_at)}`
        : null,
      providerRecovery.incidentio.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidentio.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `incident.io schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "firehydrant") {
    const details = [
      providerRecovery.firehydrant.incident_id
        ? `incident ${providerRecovery.firehydrant.incident_id}`
        : null,
      providerRecovery.firehydrant.incident_status !== "unknown"
        ? `status ${providerRecovery.firehydrant.incident_status}`
        : null,
      providerRecovery.firehydrant.severity ? `severity ${providerRecovery.firehydrant.severity}` : null,
      providerRecovery.firehydrant.priority ? `priority ${providerRecovery.firehydrant.priority}` : null,
      providerRecovery.firehydrant.team ? `team ${providerRecovery.firehydrant.team}` : null,
      providerRecovery.firehydrant.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.firehydrant.phase_graph.incident_phase}`
        : null,
      providerRecovery.firehydrant.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.firehydrant.phase_graph.workflow_phase}`
        : null,
      providerRecovery.firehydrant.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.firehydrant.phase_graph.ownership_phase}`
        : null,
      providerRecovery.firehydrant.updated_at
        ? `updated ${formatTimestamp(providerRecovery.firehydrant.updated_at)}`
        : null,
      providerRecovery.firehydrant.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.firehydrant.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `FireHydrant schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "rootly") {
    const details = [
      providerRecovery.rootly.incident_id ? `incident ${providerRecovery.rootly.incident_id}` : null,
      providerRecovery.rootly.incident_status !== "unknown"
        ? `status ${providerRecovery.rootly.incident_status}`
        : null,
      providerRecovery.rootly.severity_id ? `severity ${providerRecovery.rootly.severity_id}` : null,
      providerRecovery.rootly.private === true
        ? "private"
        : providerRecovery.rootly.private === false
          ? "public"
          : null,
      providerRecovery.rootly.slug ? `slug ${providerRecovery.rootly.slug}` : null,
      providerRecovery.rootly.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.rootly.phase_graph.incident_phase}`
        : null,
      providerRecovery.rootly.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.rootly.phase_graph.workflow_phase}`
        : null,
      providerRecovery.rootly.phase_graph.acknowledgment_phase !== "unknown"
        ? `ack ${providerRecovery.rootly.phase_graph.acknowledgment_phase}`
        : null,
      providerRecovery.rootly.updated_at
        ? `updated ${formatTimestamp(providerRecovery.rootly.updated_at)}`
        : null,
      providerRecovery.rootly.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.rootly.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Rootly schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "blameless") {
    const details = [
      providerRecovery.blameless.incident_id ? `incident ${providerRecovery.blameless.incident_id}` : null,
      providerRecovery.blameless.incident_status !== "unknown"
        ? `status ${providerRecovery.blameless.incident_status}`
        : null,
      providerRecovery.blameless.severity ? `severity ${providerRecovery.blameless.severity}` : null,
      providerRecovery.blameless.commander ? `commander ${providerRecovery.blameless.commander}` : null,
      providerRecovery.blameless.visibility ? `visibility ${providerRecovery.blameless.visibility}` : null,
      providerRecovery.blameless.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.blameless.phase_graph.incident_phase}`
        : null,
      providerRecovery.blameless.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.blameless.phase_graph.workflow_phase}`
        : null,
      providerRecovery.blameless.phase_graph.command_phase !== "unknown"
        ? `command ${providerRecovery.blameless.phase_graph.command_phase}`
        : null,
      providerRecovery.blameless.updated_at
        ? `updated ${formatTimestamp(providerRecovery.blameless.updated_at)}`
        : null,
      providerRecovery.blameless.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.blameless.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Blameless schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "xmatters") {
    const details = [
      providerRecovery.xmatters.incident_id ? `incident ${providerRecovery.xmatters.incident_id}` : null,
      providerRecovery.xmatters.incident_status !== "unknown"
        ? `status ${providerRecovery.xmatters.incident_status}`
        : null,
      providerRecovery.xmatters.priority ? `priority ${providerRecovery.xmatters.priority}` : null,
      providerRecovery.xmatters.assignee ? `assignee ${providerRecovery.xmatters.assignee}` : null,
      providerRecovery.xmatters.response_plan
        ? `response plan ${providerRecovery.xmatters.response_plan}`
        : null,
      providerRecovery.xmatters.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.xmatters.phase_graph.incident_phase}`
        : null,
      providerRecovery.xmatters.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.xmatters.phase_graph.workflow_phase}`
        : null,
      providerRecovery.xmatters.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.xmatters.phase_graph.ownership_phase}`
        : null,
      providerRecovery.xmatters.updated_at
        ? `updated ${formatTimestamp(providerRecovery.xmatters.updated_at)}`
        : null,
      providerRecovery.xmatters.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.xmatters.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `xMatters schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "servicenow") {
    const details = [
      providerRecovery.servicenow.incident_number
        ? `incident ${providerRecovery.servicenow.incident_number}`
        : null,
      providerRecovery.servicenow.incident_status !== "unknown"
        ? `status ${providerRecovery.servicenow.incident_status}`
        : null,
      providerRecovery.servicenow.priority ? `priority ${providerRecovery.servicenow.priority}` : null,
      providerRecovery.servicenow.assigned_to
        ? `assigned to ${providerRecovery.servicenow.assigned_to}`
        : null,
      providerRecovery.servicenow.assignment_group
        ? `group ${providerRecovery.servicenow.assignment_group}`
        : null,
      providerRecovery.servicenow.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.servicenow.phase_graph.incident_phase}`
        : null,
      providerRecovery.servicenow.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.servicenow.phase_graph.workflow_phase}`
        : null,
      providerRecovery.servicenow.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.servicenow.phase_graph.assignment_phase}`
        : null,
      providerRecovery.servicenow.updated_at
        ? `updated ${formatTimestamp(providerRecovery.servicenow.updated_at)}`
        : null,
      providerRecovery.servicenow.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.servicenow.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `ServiceNow schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "squadcast") {
    const details = [
      providerRecovery.squadcast.incident_id ? `incident ${providerRecovery.squadcast.incident_id}` : null,
      providerRecovery.squadcast.incident_status !== "unknown"
        ? `status ${providerRecovery.squadcast.incident_status}`
        : null,
      providerRecovery.squadcast.severity ? `severity ${providerRecovery.squadcast.severity}` : null,
      providerRecovery.squadcast.assignee ? `assignee ${providerRecovery.squadcast.assignee}` : null,
      providerRecovery.squadcast.escalation_policy
        ? `policy ${providerRecovery.squadcast.escalation_policy}`
        : null,
      providerRecovery.squadcast.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.squadcast.phase_graph.incident_phase}`
        : null,
      providerRecovery.squadcast.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.squadcast.phase_graph.workflow_phase}`
        : null,
      providerRecovery.squadcast.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.squadcast.phase_graph.ownership_phase}`
        : null,
      providerRecovery.squadcast.updated_at
        ? `updated ${formatTimestamp(providerRecovery.squadcast.updated_at)}`
        : null,
      providerRecovery.squadcast.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.squadcast.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Squadcast schema: ${details.join(" / ")}` : null;
  }
  return null;
}

export { formatProviderRecoverySchemaA };
