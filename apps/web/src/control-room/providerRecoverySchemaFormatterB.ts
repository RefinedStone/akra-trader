import { formatTimestamp } from "./ControlRoomFormatBasics";
import type { ProviderRecoverySchemaInput } from "./providerRecoverySchemaTypes";

function formatProviderRecoverySchemaB(providerRecovery: ProviderRecoverySchemaInput) {
  if (providerRecovery.provider_schema_kind === "bigpanda") {
    const details = [
      providerRecovery.bigpanda.incident_id ? `incident ${providerRecovery.bigpanda.incident_id}` : null,
      providerRecovery.bigpanda.incident_status !== "unknown"
        ? `status ${providerRecovery.bigpanda.incident_status}`
        : null,
      providerRecovery.bigpanda.severity ? `severity ${providerRecovery.bigpanda.severity}` : null,
      providerRecovery.bigpanda.assignee ? `assignee ${providerRecovery.bigpanda.assignee}` : null,
      providerRecovery.bigpanda.team ? `team ${providerRecovery.bigpanda.team}` : null,
      providerRecovery.bigpanda.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.bigpanda.phase_graph.incident_phase}`
        : null,
      providerRecovery.bigpanda.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.bigpanda.phase_graph.workflow_phase}`
        : null,
      providerRecovery.bigpanda.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.bigpanda.phase_graph.ownership_phase}`
        : null,
      providerRecovery.bigpanda.updated_at
        ? `updated ${formatTimestamp(providerRecovery.bigpanda.updated_at)}`
        : null,
      providerRecovery.bigpanda.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.bigpanda.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `BigPanda schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "grafana_oncall") {
    const details = [
      providerRecovery.grafana_oncall.incident_id
        ? `incident ${providerRecovery.grafana_oncall.incident_id}`
        : null,
      providerRecovery.grafana_oncall.incident_status !== "unknown"
        ? `status ${providerRecovery.grafana_oncall.incident_status}`
        : null,
      providerRecovery.grafana_oncall.severity
        ? `severity ${providerRecovery.grafana_oncall.severity}`
        : null,
      providerRecovery.grafana_oncall.assignee
        ? `assignee ${providerRecovery.grafana_oncall.assignee}`
        : null,
      providerRecovery.grafana_oncall.escalation_chain
        ? `chain ${providerRecovery.grafana_oncall.escalation_chain}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.grafana_oncall.phase_graph.incident_phase}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.grafana_oncall.phase_graph.workflow_phase}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.grafana_oncall.phase_graph.ownership_phase}`
        : null,
      providerRecovery.grafana_oncall.updated_at
        ? `updated ${formatTimestamp(providerRecovery.grafana_oncall.updated_at)}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.grafana_oncall.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Grafana OnCall schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "splunk_oncall") {
    const details = [
      providerRecovery.splunk_oncall.incident_id
        ? `incident ${providerRecovery.splunk_oncall.incident_id}`
        : null,
      providerRecovery.splunk_oncall.incident_status !== "unknown"
        ? `status ${providerRecovery.splunk_oncall.incident_status}`
        : null,
      providerRecovery.splunk_oncall.severity
        ? `severity ${providerRecovery.splunk_oncall.severity}`
        : null,
      providerRecovery.splunk_oncall.assignee
        ? `assignee ${providerRecovery.splunk_oncall.assignee}`
        : null,
      providerRecovery.splunk_oncall.routing_key
        ? `routing ${providerRecovery.splunk_oncall.routing_key}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.splunk_oncall.phase_graph.incident_phase}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.splunk_oncall.phase_graph.workflow_phase}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.splunk_oncall.phase_graph.ownership_phase}`
        : null,
      providerRecovery.splunk_oncall.updated_at
        ? `updated ${formatTimestamp(providerRecovery.splunk_oncall.updated_at)}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.splunk_oncall.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Splunk On-Call schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "jira_service_management") {
    const details = [
      providerRecovery.jira_service_management.incident_id
        ? `incident ${providerRecovery.jira_service_management.incident_id}`
        : null,
      providerRecovery.jira_service_management.incident_status !== "unknown"
        ? `status ${providerRecovery.jira_service_management.incident_status}`
        : null,
      providerRecovery.jira_service_management.priority
        ? `priority ${providerRecovery.jira_service_management.priority}`
        : null,
      providerRecovery.jira_service_management.assignee
        ? `assignee ${providerRecovery.jira_service_management.assignee}`
        : null,
      providerRecovery.jira_service_management.service_project
        ? `project ${providerRecovery.jira_service_management.service_project}`
        : null,
      providerRecovery.jira_service_management.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.jira_service_management.phase_graph.incident_phase}`
        : null,
      providerRecovery.jira_service_management.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.jira_service_management.phase_graph.workflow_phase}`
        : null,
      providerRecovery.jira_service_management.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.jira_service_management.phase_graph.assignment_phase}`
        : null,
      providerRecovery.jira_service_management.updated_at
        ? `updated ${formatTimestamp(providerRecovery.jira_service_management.updated_at)}`
        : null,
      providerRecovery.jira_service_management.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.jira_service_management.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `Jira Service Management schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "pagertree") {
    const details = [
      providerRecovery.pagertree.incident_id ? `incident ${providerRecovery.pagertree.incident_id}` : null,
      providerRecovery.pagertree.incident_status !== "unknown"
        ? `status ${providerRecovery.pagertree.incident_status}`
        : null,
      providerRecovery.pagertree.urgency ? `urgency ${providerRecovery.pagertree.urgency}` : null,
      providerRecovery.pagertree.assignee ? `assignee ${providerRecovery.pagertree.assignee}` : null,
      providerRecovery.pagertree.team ? `team ${providerRecovery.pagertree.team}` : null,
      providerRecovery.pagertree.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.pagertree.phase_graph.incident_phase}`
        : null,
      providerRecovery.pagertree.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.pagertree.phase_graph.workflow_phase}`
        : null,
      providerRecovery.pagertree.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.pagertree.phase_graph.ownership_phase}`
        : null,
      providerRecovery.pagertree.updated_at
        ? `updated ${formatTimestamp(providerRecovery.pagertree.updated_at)}`
        : null,
      providerRecovery.pagertree.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.pagertree.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `PagerTree schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "alertops") {
    const details = [
      providerRecovery.alertops.incident_id ? `incident ${providerRecovery.alertops.incident_id}` : null,
      providerRecovery.alertops.incident_status !== "unknown"
        ? `status ${providerRecovery.alertops.incident_status}`
        : null,
      providerRecovery.alertops.priority ? `priority ${providerRecovery.alertops.priority}` : null,
      providerRecovery.alertops.owner ? `owner ${providerRecovery.alertops.owner}` : null,
      providerRecovery.alertops.service ? `service ${providerRecovery.alertops.service}` : null,
      providerRecovery.alertops.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.alertops.phase_graph.incident_phase}`
        : null,
      providerRecovery.alertops.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.alertops.phase_graph.workflow_phase}`
        : null,
      providerRecovery.alertops.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.alertops.phase_graph.ownership_phase}`
        : null,
      providerRecovery.alertops.updated_at
        ? `updated ${formatTimestamp(providerRecovery.alertops.updated_at)}`
        : null,
      providerRecovery.alertops.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.alertops.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `AlertOps schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "signl4") {
    const details = [
      providerRecovery.signl4.alert_id ? `alert ${providerRecovery.signl4.alert_id}` : null,
      providerRecovery.signl4.alert_status !== "unknown"
        ? `status ${providerRecovery.signl4.alert_status}`
        : null,
      providerRecovery.signl4.priority ? `priority ${providerRecovery.signl4.priority}` : null,
      providerRecovery.signl4.team ? `team ${providerRecovery.signl4.team}` : null,
      providerRecovery.signl4.assignee ? `assignee ${providerRecovery.signl4.assignee}` : null,
      providerRecovery.signl4.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.signl4.phase_graph.alert_phase}`
        : null,
      providerRecovery.signl4.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.signl4.phase_graph.workflow_phase}`
        : null,
      providerRecovery.signl4.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.signl4.phase_graph.ownership_phase}`
        : null,
      providerRecovery.signl4.phase_graph.priority_phase !== "unknown"
        ? `priority phase ${providerRecovery.signl4.phase_graph.priority_phase}`
        : null,
      providerRecovery.signl4.phase_graph.team_phase !== "unknown"
        ? `team phase ${providerRecovery.signl4.phase_graph.team_phase}`
        : null,
      providerRecovery.signl4.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.signl4.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `SIGNL4 schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "ilert") {
    const details = [
      providerRecovery.ilert.alert_id ? `alert ${providerRecovery.ilert.alert_id}` : null,
      providerRecovery.ilert.alert_status !== "unknown"
        ? `status ${providerRecovery.ilert.alert_status}`
        : null,
      providerRecovery.ilert.priority ? `priority ${providerRecovery.ilert.priority}` : null,
      providerRecovery.ilert.escalation_policy
        ? `policy ${providerRecovery.ilert.escalation_policy}`
        : null,
      providerRecovery.ilert.assignee ? `assignee ${providerRecovery.ilert.assignee}` : null,
      providerRecovery.ilert.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.ilert.phase_graph.alert_phase}`
        : null,
      providerRecovery.ilert.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.ilert.phase_graph.workflow_phase}`
        : null,
      providerRecovery.ilert.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.ilert.phase_graph.ownership_phase}`
        : null,
      providerRecovery.ilert.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.ilert.phase_graph.escalation_phase}`
        : null,
      providerRecovery.ilert.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.ilert.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `iLert schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "betterstack") {
    const details = [
      providerRecovery.betterstack.alert_id ? `alert ${providerRecovery.betterstack.alert_id}` : null,
      providerRecovery.betterstack.alert_status !== "unknown"
        ? `status ${providerRecovery.betterstack.alert_status}`
        : null,
      providerRecovery.betterstack.priority
        ? `priority ${providerRecovery.betterstack.priority}`
        : null,
      providerRecovery.betterstack.escalation_policy
        ? `policy ${providerRecovery.betterstack.escalation_policy}`
        : null,
      providerRecovery.betterstack.assignee
        ? `assignee ${providerRecovery.betterstack.assignee}`
        : null,
      providerRecovery.betterstack.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.betterstack.phase_graph.alert_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.betterstack.phase_graph.workflow_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.betterstack.phase_graph.ownership_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.betterstack.phase_graph.escalation_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.betterstack.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Better Stack schema: ${details.join(" / ")}` : null;
  }
  return null;
}

export { formatProviderRecoverySchemaB };
