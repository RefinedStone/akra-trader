import type { OperatorAlertMarketContextProvenance, OperatorAlertPrimaryFocus } from "./operatorVisibility";

export type OperatorIncidentEventEntry = {
event_id: string; alert_id: string; timestamp: string; kind: string;
severity: string; summary: string; detail: string; run_id?: string | null;
session_id?: string | null; symbol?: string | null;
  symbols: string[];
timeframe?: string | null; primary_focus?: OperatorAlertPrimaryFocus | null; source: string; paging_policy_id: string;
paging_provider?: string | null;
  delivery_targets: string[];
  escalation_targets: string[];
delivery_state: string; acknowledgment_state: string; acknowledged_at?: string | null; acknowledged_by?: string | null;
acknowledgment_reason?: string | null; escalation_level: number; escalation_state: string; last_escalated_at?: string | null;
last_escalated_by?: string | null; escalation_reason?: string | null; lineage_evidence_pack_id?: string | null; lineage_evidence_retention_expires_at?: string | null;
lineage_evidence_summary?: string | null; next_escalation_at?: string | null; external_provider?: string | null; external_reference?: string | null;
provider_workflow_reference?: string | null; external_status: string; external_last_synced_at?: string | null; paging_status: string;
provider_workflow_state: string; provider_workflow_action?: string | null; provider_workflow_last_attempted_at?: string | null;
  remediation: {
state: string; kind?: string | null; owner?: string | null; summary?: string | null;
detail?: string | null; runbook?: string | null; requested_at?: string | null; requested_by?: string | null;
last_attempted_at?: string | null; provider?: string | null; reference?: string | null; provider_payload: Record<string, unknown>;
provider_payload_updated_at?: string | null;
    provider_recovery: {
lifecycle_state: string; provider?: string | null; job_id?: string | null; reference?: string | null;
workflow_reference?: string | null; summary?: string | null; detail?: string | null;
      channels: string[];
      symbols: string[];
timeframe?: string | null; market_context_provenance?: OperatorAlertMarketContextProvenance | null; updated_at?: string | null;
      verification: {
state: string; checked_at?: string | null; summary?: string | null;
        issues: string[];
      };
      telemetry: {
source: string; state: string; progress_percent?: number | null; attempt_count: number;
current_step?: string | null; last_message?: string | null; last_error?: string | null; external_run_id?: string | null;
job_url?: string | null; started_at?: string | null; finished_at?: string | null; updated_at?: string | null;
      };
      status_machine: {
state: string; workflow_state: string; workflow_action?: string | null; job_state: string;
sync_state: string; last_event_kind?: string | null; last_event_at?: string | null; last_detail?: string | null;
attempt_number: number;
      };
provider_schema_kind?: string | null;
      pagerduty: {
incident_id?: string | null; incident_key?: string | null; incident_status: string; urgency?: string | null;
service_id?: string | null; service_summary?: string | null; escalation_policy_id?: string | null; escalation_policy_summary?: string | null;
html_url?: string | null; last_status_change_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; responder_phase: string; urgency_phase: string;
last_transition_at?: string | null;
        };
      };
      opsgenie: {
alert_id?: string | null; alias?: string | null; alert_status: string; priority?: string | null;
owner?: string | null; acknowledged?: boolean | null; seen?: boolean | null; tiny_id?: string | null;
        teams: string[];
updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; acknowledgment_phase: string; ownership_phase: string;
visibility_phase: string; last_transition_at?: string | null;
        };
      };
      incidentio: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
mode?: string | null; visibility?: string | null; assignee?: string | null; url?: string | null;
updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; assignment_phase: string; visibility_phase: string;
severity_phase: string; last_transition_at?: string | null;
        };
      };
      firehydrant: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
priority?: string | null; team?: string | null; runbook?: string | null; url?: string | null;
updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; severity_phase: string;
priority_phase: string; last_transition_at?: string | null;
        };
      };
      rootly: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity_id?: string | null;
private?: boolean | null; slug?: string | null; url?: string | null; acknowledged_at?: string | null;
updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; acknowledgment_phase: string; visibility_phase: string;
severity_phase: string; last_transition_at?: string | null;
        };
      };
      blameless: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
commander?: string | null; visibility?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; command_phase: string; visibility_phase: string;
severity_phase: string; last_transition_at?: string | null;
        };
      };
      xmatters: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; priority?: string | null;
assignee?: string | null; response_plan?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
response_plan_phase: string; last_transition_at?: string | null;
        };
      };
      servicenow: {
incident_number?: string | null; external_reference?: string | null; incident_status: string; priority?: string | null;
assigned_to?: string | null; assignment_group?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; assignment_phase: string; priority_phase: string;
group_phase: string; last_transition_at?: string | null;
        };
      };
      squadcast: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
assignee?: string | null; escalation_policy?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; severity_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      bigpanda: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
assignee?: string | null; team?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; severity_phase: string;
team_phase: string; last_transition_at?: string | null;
        };
      };
      grafana_oncall: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
assignee?: string | null; escalation_chain?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; severity_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      splunk_oncall: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
assignee?: string | null; routing_key?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; severity_phase: string;
routing_phase: string; last_transition_at?: string | null;
        };
      };
      jira_service_management: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; priority?: string | null;
assignee?: string | null; service_project?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; assignment_phase: string; priority_phase: string;
project_phase: string; last_transition_at?: string | null;
        };
      };
      pagertree: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; urgency?: string | null;
assignee?: string | null; team?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; urgency_phase: string;
team_phase: string; last_transition_at?: string | null;
        };
      };
      alertops: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; priority?: string | null;
owner?: string | null; service?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
service_phase: string; last_transition_at?: string | null;
        };
      };
      signl4: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
team?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
team_phase: string; last_transition_at?: string | null;
        };
      };
      ilert: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      betterstack: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      onpage: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      allquiet: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      moogsoft: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      spikesh: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      dutycalls: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      incidenthub: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      resolver: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      openduty: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      cabot: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      haloitsm: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      incidentmanagerio: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      oneuptime: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      squzy: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      crisescontrol: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      freshservice: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      freshdesk: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      happyfox: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      zendesk: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      zohodesk: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      helpscout: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      kayako: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      intercom: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      front: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      servicedeskplus: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      sysaid: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      bmchelix: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      solarwindsservicedesk: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      topdesk: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      invgateservicedesk: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      opsramp: {
alert_id?: string | null; external_reference?: string | null; alert_status: string; priority?: string | null;
escalation_policy?: string | null; assignee?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
alert_phase: string; workflow_phase: string; ownership_phase: string; priority_phase: string;
escalation_phase: string; last_transition_at?: string | null;
        };
      };
      zenduty: {
incident_id?: string | null; external_reference?: string | null; incident_status: string; severity?: string | null;
assignee?: string | null; service?: string | null; url?: string | null; updated_at?: string | null;
        phase_graph: {
incident_phase: string; workflow_phase: string; ownership_phase: string; severity_phase: string;
service_phase: string; last_transition_at?: string | null;
        };
      };
    };
  };
};
