import { formatTimestamp } from "./ControlRoomFormatBasics";
import type { ProviderRecoverySchemaInput } from "./providerRecoverySchemaTypes";

function formatProviderRecoverySchemaC(providerRecovery: ProviderRecoverySchemaInput) {
  if (providerRecovery.provider_schema_kind === "onpage") {
    const details = [
      providerRecovery.onpage.alert_id ? `alert ${providerRecovery.onpage.alert_id}` : null,
      providerRecovery.onpage.alert_status !== "unknown"
        ? `status ${providerRecovery.onpage.alert_status}`
        : null,
      providerRecovery.onpage.priority ? `priority ${providerRecovery.onpage.priority}` : null,
      providerRecovery.onpage.escalation_policy
        ? `policy ${providerRecovery.onpage.escalation_policy}`
        : null,
      providerRecovery.onpage.assignee ? `assignee ${providerRecovery.onpage.assignee}` : null,
      providerRecovery.onpage.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.onpage.phase_graph.alert_phase}`
        : null,
      providerRecovery.onpage.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.onpage.phase_graph.workflow_phase}`
        : null,
      providerRecovery.onpage.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.onpage.phase_graph.ownership_phase}`
        : null,
      providerRecovery.onpage.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.onpage.phase_graph.escalation_phase}`
        : null,
      providerRecovery.onpage.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.onpage.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OnPage schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "allquiet") {
    const details = [
      providerRecovery.allquiet.alert_id ? `alert ${providerRecovery.allquiet.alert_id}` : null,
      providerRecovery.allquiet.alert_status !== "unknown"
        ? `status ${providerRecovery.allquiet.alert_status}`
        : null,
      providerRecovery.allquiet.priority ? `priority ${providerRecovery.allquiet.priority}` : null,
      providerRecovery.allquiet.escalation_policy
        ? `policy ${providerRecovery.allquiet.escalation_policy}`
        : null,
      providerRecovery.allquiet.assignee ? `assignee ${providerRecovery.allquiet.assignee}` : null,
      providerRecovery.allquiet.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.allquiet.phase_graph.alert_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.allquiet.phase_graph.workflow_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.allquiet.phase_graph.ownership_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.allquiet.phase_graph.escalation_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.allquiet.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `All Quiet schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "moogsoft") {
    const details = [
      providerRecovery.moogsoft.alert_id ? `alert ${providerRecovery.moogsoft.alert_id}` : null,
      providerRecovery.moogsoft.alert_status !== "unknown"
        ? `status ${providerRecovery.moogsoft.alert_status}`
        : null,
      providerRecovery.moogsoft.priority ? `priority ${providerRecovery.moogsoft.priority}` : null,
      providerRecovery.moogsoft.escalation_policy
        ? `policy ${providerRecovery.moogsoft.escalation_policy}`
        : null,
      providerRecovery.moogsoft.assignee ? `assignee ${providerRecovery.moogsoft.assignee}` : null,
      providerRecovery.moogsoft.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.moogsoft.phase_graph.alert_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.moogsoft.phase_graph.workflow_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.moogsoft.phase_graph.ownership_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.moogsoft.phase_graph.escalation_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.moogsoft.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Moogsoft schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "spikesh") {
    const details = [
      providerRecovery.spikesh.alert_id ? `alert ${providerRecovery.spikesh.alert_id}` : null,
      providerRecovery.spikesh.alert_status !== "unknown"
        ? `status ${providerRecovery.spikesh.alert_status}`
        : null,
      providerRecovery.spikesh.priority ? `priority ${providerRecovery.spikesh.priority}` : null,
      providerRecovery.spikesh.escalation_policy
        ? `policy ${providerRecovery.spikesh.escalation_policy}`
        : null,
      providerRecovery.spikesh.assignee ? `assignee ${providerRecovery.spikesh.assignee}` : null,
      providerRecovery.spikesh.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.spikesh.phase_graph.alert_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.spikesh.phase_graph.workflow_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.spikesh.phase_graph.ownership_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.spikesh.phase_graph.escalation_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.spikesh.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Spike.sh schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "dutycalls") {
    const details = [
      providerRecovery.dutycalls.alert_id ? `alert ${providerRecovery.dutycalls.alert_id}` : null,
      providerRecovery.dutycalls.alert_status !== "unknown"
        ? `status ${providerRecovery.dutycalls.alert_status}`
        : null,
      providerRecovery.dutycalls.priority ? `priority ${providerRecovery.dutycalls.priority}` : null,
      providerRecovery.dutycalls.escalation_policy
        ? `policy ${providerRecovery.dutycalls.escalation_policy}`
        : null,
      providerRecovery.dutycalls.assignee ? `assignee ${providerRecovery.dutycalls.assignee}` : null,
      providerRecovery.dutycalls.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.dutycalls.phase_graph.alert_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.dutycalls.phase_graph.workflow_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.dutycalls.phase_graph.ownership_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.dutycalls.phase_graph.escalation_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.dutycalls.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `DutyCalls schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidenthub") {
    const details = [
      providerRecovery.incidenthub.alert_id ? `alert ${providerRecovery.incidenthub.alert_id}` : null,
      providerRecovery.incidenthub.alert_status !== "unknown"
        ? `status ${providerRecovery.incidenthub.alert_status}`
        : null,
      providerRecovery.incidenthub.priority ? `priority ${providerRecovery.incidenthub.priority}` : null,
      providerRecovery.incidenthub.escalation_policy
        ? `policy ${providerRecovery.incidenthub.escalation_policy}`
        : null,
      providerRecovery.incidenthub.assignee ? `assignee ${providerRecovery.incidenthub.assignee}` : null,
      providerRecovery.incidenthub.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.incidenthub.phase_graph.alert_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidenthub.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.incidenthub.phase_graph.ownership_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.incidenthub.phase_graph.escalation_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidenthub.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `IncidentHub schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "resolver") {
    const details = [
      providerRecovery.resolver.alert_id ? `alert ${providerRecovery.resolver.alert_id}` : null,
      providerRecovery.resolver.alert_status !== "unknown"
        ? `status ${providerRecovery.resolver.alert_status}`
        : null,
      providerRecovery.resolver.priority ? `priority ${providerRecovery.resolver.priority}` : null,
      providerRecovery.resolver.escalation_policy
        ? `policy ${providerRecovery.resolver.escalation_policy}`
        : null,
      providerRecovery.resolver.assignee ? `assignee ${providerRecovery.resolver.assignee}` : null,
      providerRecovery.resolver.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.resolver.phase_graph.alert_phase}`
        : null,
      providerRecovery.resolver.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.resolver.phase_graph.workflow_phase}`
        : null,
      providerRecovery.resolver.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.resolver.phase_graph.ownership_phase}`
        : null,
      providerRecovery.resolver.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.resolver.phase_graph.escalation_phase}`
        : null,
      providerRecovery.resolver.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.resolver.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Resolver schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "openduty") {
    const details = [
      providerRecovery.openduty.alert_id ? `alert ${providerRecovery.openduty.alert_id}` : null,
      providerRecovery.openduty.alert_status !== "unknown"
        ? `status ${providerRecovery.openduty.alert_status}`
        : null,
      providerRecovery.openduty.priority ? `priority ${providerRecovery.openduty.priority}` : null,
      providerRecovery.openduty.escalation_policy
        ? `policy ${providerRecovery.openduty.escalation_policy}`
        : null,
      providerRecovery.openduty.assignee ? `assignee ${providerRecovery.openduty.assignee}` : null,
      providerRecovery.openduty.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.openduty.phase_graph.alert_phase}`
        : null,
      providerRecovery.openduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.openduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.openduty.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.openduty.phase_graph.ownership_phase}`
        : null,
      providerRecovery.openduty.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.openduty.phase_graph.escalation_phase}`
        : null,
      providerRecovery.openduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.openduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OpenDuty schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "cabot") {
    const details = [
      providerRecovery.cabot.alert_id ? `alert ${providerRecovery.cabot.alert_id}` : null,
      providerRecovery.cabot.alert_status !== "unknown"
        ? `status ${providerRecovery.cabot.alert_status}`
        : null,
      providerRecovery.cabot.priority ? `priority ${providerRecovery.cabot.priority}` : null,
      providerRecovery.cabot.escalation_policy
        ? `policy ${providerRecovery.cabot.escalation_policy}`
        : null,
      providerRecovery.cabot.assignee ? `assignee ${providerRecovery.cabot.assignee}` : null,
      providerRecovery.cabot.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.cabot.phase_graph.alert_phase}`
        : null,
      providerRecovery.cabot.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.cabot.phase_graph.workflow_phase}`
        : null,
      providerRecovery.cabot.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.cabot.phase_graph.ownership_phase}`
        : null,
      providerRecovery.cabot.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.cabot.phase_graph.escalation_phase}`
        : null,
      providerRecovery.cabot.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.cabot.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Cabot schema: ${details.join(" / ")}` : null;
  }
  return null;
}

export { formatProviderRecoverySchemaC };
