function formatTimestamp(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value;
}

function formatProviderRecoverySchema(providerRecovery: {
  provider_schema_kind?: string | null;
  pagerduty: {
    incident_id?: string | null;
    incident_key?: string | null;
    incident_status: string;
    urgency?: string | null;
    service_summary?: string | null;
    escalation_policy_summary?: string | null;
    last_status_change_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      responder_phase: string;
      urgency_phase: string;
      last_transition_at?: string | null;
    };
  };
  opsgenie: {
    alert_id?: string | null;
    alias?: string | null;
    alert_status: string;
    priority?: string | null;
    owner?: string | null;
    teams: string[];
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      acknowledgment_phase: string;
      ownership_phase: string;
      visibility_phase: string;
      last_transition_at?: string | null;
    };
  };
  incidentio: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    mode?: string | null;
    visibility?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      assignment_phase: string;
      visibility_phase: string;
      severity_phase: string;
      last_transition_at?: string | null;
    };
  };
  firehydrant: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    priority?: string | null;
    team?: string | null;
    runbook?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      priority_phase: string;
      last_transition_at?: string | null;
    };
  };
  rootly: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity_id?: string | null;
    private?: boolean | null;
    slug?: string | null;
    url?: string | null;
    acknowledged_at?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      acknowledgment_phase: string;
      visibility_phase: string;
      severity_phase: string;
      last_transition_at?: string | null;
    };
  };
  blameless: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    commander?: string | null;
    visibility?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      command_phase: string;
      visibility_phase: string;
      severity_phase: string;
      last_transition_at?: string | null;
    };
  };
  xmatters: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    assignee?: string | null;
    response_plan?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      response_plan_phase: string;
      last_transition_at?: string | null;
    };
  };
  servicenow: {
    incident_number?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    assigned_to?: string | null;
    assignment_group?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      assignment_phase: string;
      priority_phase: string;
      group_phase: string;
      last_transition_at?: string | null;
    };
  };
  squadcast: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    escalation_policy?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  bigpanda: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    team?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      team_phase: string;
      last_transition_at?: string | null;
    };
  };
  grafana_oncall: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    escalation_chain?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  splunk_oncall: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    routing_key?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      routing_phase: string;
      last_transition_at?: string | null;
    };
  };
  jira_service_management: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    assignee?: string | null;
    service_project?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      assignment_phase: string;
      priority_phase: string;
      project_phase: string;
      last_transition_at?: string | null;
    };
  };
  pagertree: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    urgency?: string | null;
    assignee?: string | null;
    team?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      urgency_phase: string;
      team_phase: string;
      last_transition_at?: string | null;
    };
  };
  alertops: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    priority?: string | null;
    owner?: string | null;
    service?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      service_phase: string;
      last_transition_at?: string | null;
    };
  };
  signl4: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    team?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      team_phase: string;
      last_transition_at?: string | null;
    };
  };
  ilert: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  betterstack: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  onpage: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  allquiet: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  moogsoft: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  spikesh: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  dutycalls: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  incidenthub: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  resolver: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  openduty: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  cabot: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  haloitsm: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  incidentmanagerio: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  oneuptime: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  squzy: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  crisescontrol: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  freshservice: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  freshdesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  happyfox: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  zendesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  zohodesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  helpscout: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  kayako: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  intercom: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  front: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  servicedeskplus: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  sysaid: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  bmchelix: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  solarwindsservicedesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  topdesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  invgateservicedesk: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  opsramp: {
    alert_id?: string | null;
    external_reference?: string | null;
    alert_status: string;
    priority?: string | null;
    escalation_policy?: string | null;
    assignee?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      alert_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      priority_phase: string;
      escalation_phase: string;
      last_transition_at?: string | null;
    };
  };
  zenduty: {
    incident_id?: string | null;
    external_reference?: string | null;
    incident_status: string;
    severity?: string | null;
    assignee?: string | null;
    service?: string | null;
    url?: string | null;
    updated_at?: string | null;
    phase_graph: {
      incident_phase: string;
      workflow_phase: string;
      ownership_phase: string;
      severity_phase: string;
      service_phase: string;
      last_transition_at?: string | null;
    };
  };
}) {
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

function formatProviderRecoveryTelemetry(providerRecovery: {
  telemetry: {
    source: string;
    state: string;
    progress_percent?: number | null;
    attempt_count: number;
    current_step?: string | null;
    last_message?: string | null;
    last_error?: string | null;
    external_run_id?: string | null;
    updated_at?: string | null;
  };
}) {
  const details = [
    providerRecovery.telemetry.source !== "unknown"
      ? `source ${providerRecovery.telemetry.source}`
      : null,
    providerRecovery.telemetry.state !== "unknown"
      ? `state ${providerRecovery.telemetry.state}`
      : null,
    providerRecovery.telemetry.progress_percent != null
      ? `progress ${providerRecovery.telemetry.progress_percent}%`
      : null,
    providerRecovery.telemetry.attempt_count
      ? `attempts ${providerRecovery.telemetry.attempt_count}`
      : null,
    providerRecovery.telemetry.current_step
      ? `step ${providerRecovery.telemetry.current_step}`
      : null,
    providerRecovery.telemetry.external_run_id
      ? `run ${providerRecovery.telemetry.external_run_id}`
      : null,
    providerRecovery.telemetry.updated_at
      ? `updated ${formatTimestamp(providerRecovery.telemetry.updated_at)}`
      : null,
    providerRecovery.telemetry.last_error
      ? `error ${providerRecovery.telemetry.last_error}`
      : providerRecovery.telemetry.last_message
        ? `message ${providerRecovery.telemetry.last_message}`
        : null,
  ].filter(Boolean);
  return details.length ? `Recovery telemetry: ${details.join(" / ")}` : null;
}

function shortenIdentifier(value: string, maxLength = 18) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3)}...`;
}

function truncateLabel(value: string, maxLength = 56) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3)}...`;
}

function formatRange(start?: string | null, end?: string | null) {
  if (!start && !end) {
    return "open-ended";
  }
  return `${formatTimestamp(start)} -> ${formatTimestamp(end)}`;
}

const benchmarkArtifactSummaryOrder = [
  "strategy_name",
  "run_id",
  "exchange",
  "stake_currency",
  "timeframe",
  "timerange",
  "generated_at",
  "backtest_start_at",
  "backtest_end_at",
  "pair_count",
  "trade_count",
  "profit_total_pct",
  "profit_total_abs",
  "max_drawdown_pct",
  "market_change_pct",
  "manifest_count",
  "snapshot_count",
] as const;

const benchmarkArtifactSummaryLabels: Record<string, string> = {
  headline: "Headline",
  market_context: "Market read",
  portfolio_context: "Portfolio read",
  signal_context: "Signal read",
  rejection_context: "Rejections",
  exit_context: "Exit read",
  pair_context: "Pair read",
  strategy_name: "Strategy",
  run_id: "Run ID",
  exchange: "Exchange",
  stake_currency: "Stake",
  timeframe: "TF",
  timerange: "Timerange",
  generated_at: "Generated",
  backtest_start_at: "Backtest start",
  backtest_end_at: "Backtest end",
  pair_count: "Pairs",
  trade_count: "Trades",
  profit_total_pct: "Total return",
  profit_total_abs: "Total PnL",
  max_drawdown_pct: "Max DD",
  market_change_pct: "Market move",
  manifest_count: "Manifests",
  snapshot_count: "Snapshots",
  timeframe_detail: "TF detail",
  notes: "Notes",
  win_rate_pct: "Win rate",
  date: "Date",
  duration: "Duration",
  drawdown_start: "DD start",
  drawdown_end: "DD end",
  start_balance: "Start balance",
  end_balance: "End balance",
  high_balance: "High balance",
  low_balance: "Low balance",
  sharpe: "Sharpe",
  sortino: "Sortino",
  calmar: "Calmar",
  member_count: "Members",
  entry_preview: "Entries",
  market_change_export_count: "Market exports",
  wallet_export_count: "Wallet exports",
  signal_export_count: "Signal exports",
  rejected_export_count: "Rejected exports",
  exited_export_count: "Exited exports",
  strategy_source_count: "Strategy sources",
  strategy_param_count: "Strategy params",
  result_json_entry: "Result JSON",
  config_json_entry: "Config JSON",
  strategy: "Strategy",
  trading_mode: "Trading mode",
  margin_mode: "Margin mode",
  max_open_trades: "Max open trades",
  export: "Export",
  source_files: "Source files",
  parameter_files: "Parameter files",
  strategy_names: "Strategy names",
  parameter_keys: "Parameter keys",
  entry: "Entry",
  row_count: "Rows",
  total_row_count: "Total rows",
  frame_count: "Frames",
  column_count: "Columns",
  columns: "Column list",
  date_start: "Start",
  date_end: "End",
  export_count: "Exports",
  strategies: "Strategies",
  currencies: "Currencies",
  currency_count: "Currency count",
  entries: "Entries",
  unreadable_entries: "Unreadable",
  inspection_status: "Inspection",
  pair_change_preview: "Pair moves",
  best_pair: "Best pair",
  best_pair_change_pct: "Best pair move",
  worst_pair: "Worst pair",
  worst_pair_change_pct: "Worst pair move",
  positive_pair_count: "Positive pairs",
  negative_pair_count: "Negative pairs",
  start_value: "Start value",
  end_value: "End value",
  change_pct: "Change",
  total_quote_start: "Quote start",
  total_quote_end: "Quote end",
  total_quote_high: "Quote high",
  total_quote_low: "Quote low",
  currency_quote_preview: "Currency quote preview",
  latest_balance: "Latest balance",
  latest_quote_value: "Latest quote value",
  strategy_row_preview: "Strategy rows",
  pair_row_preview: "Pair rows",
  semantic_columns: "Semantic columns",
  enter_tag_counts: "Entry tag counts",
  reason_counts: "Reason counts",
  exit_reason_counts: "Exit reason counts",
};

const benchmarkArtifactSectionOrder = [
  "benchmark_story",
  "zip_contents",
  "zip_config",
  "zip_strategy_bundle",
  "zip_market_change",
  "zip_wallet_exports",
  "zip_signal_exports",
  "zip_rejected_exports",
  "zip_exited_exports",
  "metadata",
  "strategy_comparison",
  "pair_metrics",
  "pair_extremes",
  "enter_tag_metrics",
  "exit_reason_metrics",
  "mixed_tag_metrics",
  "left_open_metrics",
  "periodic_breakdown",
  "daily_profit",
  "wallet_stats",
] as const;

const benchmarkArtifactSectionLabels: Record<string, string> = {
  benchmark_story: "Benchmark narrative",
  zip_contents: "Zip contents",
  zip_config: "Embedded config",
  zip_strategy_bundle: "Strategy bundle",
  zip_market_change: "Market change export",
  zip_wallet_exports: "Wallet exports",
  zip_signal_exports: "Signal exports",
  zip_rejected_exports: "Rejected exports",
  zip_exited_exports: "Exited exports",
  metadata: "Metadata",
  strategy_comparison: "Strategy comparison",
  pair_metrics: "Pair metrics",
  pair_extremes: "Pair extremes",
  enter_tag_metrics: "Entry tags",
  exit_reason_metrics: "Exit reasons",
  mixed_tag_metrics: "Mixed tags",
  left_open_metrics: "Left open",
  periodic_breakdown: "Periodic breakdown",
  daily_profit: "Daily profit",
  wallet_stats: "Wallet stats",
};

function formatBenchmarkArtifactSummaryEntries(summary: Record<string, unknown>) {
  return Object.entries(summary)
    .map(([key, value]) => [key, formatBenchmarkArtifactSummaryValue(key, value)] as const)
    .filter(([, value]) => value !== null)
    .sort(([leftKey], [rightKey]) => {
      const leftIndex = benchmarkArtifactSummarySortIndex(leftKey);
      const rightIndex = benchmarkArtifactSummarySortIndex(rightKey);
      if (leftIndex === rightIndex) {
        return leftKey.localeCompare(rightKey);
      }
      return leftIndex - rightIndex;
    });
}

function benchmarkArtifactSummarySortIndex(key: string) {
  const index = benchmarkArtifactSummaryOrder.indexOf(key as (typeof benchmarkArtifactSummaryOrder)[number]);
  if (index >= 0) {
    return index;
  }
  return benchmarkArtifactSummaryOrder.length + 100;
}

function formatBenchmarkArtifactSummaryLabel(key: string) {
  return benchmarkArtifactSummaryLabels[key] ?? key.replaceAll("_", " ");
}

function formatBenchmarkArtifactSummaryValue(key: string, value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (typeof value === "boolean") {
    return value ? "yes" : "no";
  }
  if (typeof value === "number") {
    if (key.endsWith("_pct")) {
      return `${value}%`;
    }
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function formatBenchmarkArtifactSectionEntries(sections: Record<string, Record<string, unknown>>) {
  return Object.entries(sections)
    .map(([key, section]) => [key, formatBenchmarkArtifactSectionLines(section)] as const)
    .filter(([, lines]) => lines.length > 0)
    .sort(([leftKey], [rightKey]) => {
      const leftIndex = benchmarkArtifactSectionSortIndex(leftKey);
      const rightIndex = benchmarkArtifactSectionSortIndex(rightKey);
      if (leftIndex === rightIndex) {
        return leftKey.localeCompare(rightKey);
      }
      return leftIndex - rightIndex;
    });
}

function benchmarkArtifactSectionSortIndex(key: string) {
  const index = benchmarkArtifactSectionOrder.indexOf(key as (typeof benchmarkArtifactSectionOrder)[number]);
  if (index >= 0) {
    return index;
  }
  return benchmarkArtifactSectionOrder.length + 100;
}

function formatBenchmarkArtifactSectionLabel(key: string) {
  return benchmarkArtifactSectionLabels[key] ?? key.replaceAll("_", " ");
}

function formatBenchmarkArtifactSectionLines(section: Record<string, unknown>) {
  return Object.entries(section)
    .map(([key, value]) => {
      const inlineValue = formatBenchmarkArtifactSectionValue(value);
      if (inlineValue === null) {
        return null;
      }
      return `${formatBenchmarkArtifactSummaryLabel(key)}: ${inlineValue}`;
    })
    .filter((line): line is string => line !== null);
}

function formatBenchmarkArtifactSectionValue(value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (Array.isArray(value)) {
    if (!value.length) {
      return null;
    }
    const preview = value.slice(0, 3).map((item) => formatBenchmarkArtifactInlineValue(item)).join(" | ");
    if (value.length > 3) {
      return `${preview} | +${value.length - 3} more`;
    }
    return preview;
  }
  if (typeof value === "object") {
    return formatBenchmarkArtifactInlineValue(value);
  }
  return String(value);
}

function formatBenchmarkArtifactInlineValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "n/a";
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatBenchmarkArtifactInlineValue(item)).join(", ");
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .filter(([key]) => !key.startsWith("__"))
      .map(([key, nestedValue]) => {
        const formattedValue = formatBenchmarkArtifactSummaryValue(key, nestedValue);
        if (formattedValue === null) {
          return null;
        }
        return `${formatBenchmarkArtifactSummaryLabel(key)}=${formattedValue}`;
      })
      .filter((entry): entry is string => entry !== null)
      .join(", ");
  }
  return String(value);
}


export {
  formatTimestamp,
  formatProviderRecoverySchema,
  formatProviderRecoveryTelemetry,
  shortenIdentifier,
  truncateLabel,
  formatRange,
  benchmarkArtifactSummaryOrder,
  benchmarkArtifactSummaryLabels,
  benchmarkArtifactSectionOrder,
  benchmarkArtifactSectionLabels,
  formatBenchmarkArtifactSummaryEntries,
  benchmarkArtifactSummarySortIndex,
  formatBenchmarkArtifactSummaryLabel,
  formatBenchmarkArtifactSummaryValue,
  formatBenchmarkArtifactSectionEntries,
  benchmarkArtifactSectionSortIndex,
  formatBenchmarkArtifactSectionLabel,
  formatBenchmarkArtifactSectionLines,
  formatBenchmarkArtifactSectionValue,
  formatBenchmarkArtifactInlineValue
};
