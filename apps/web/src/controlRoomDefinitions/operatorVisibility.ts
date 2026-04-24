export type OperatorAlertMarketContextFieldProvenance = {
  scope?: string | null;
  path?: string | null;
};

export type OperatorAlertMarketContextProvenance = {
  provider?: string | null;
  vendor_field?: string | null;
  symbol?: OperatorAlertMarketContextFieldProvenance | null;
  symbols?: OperatorAlertMarketContextFieldProvenance | null;
  timeframe?: OperatorAlertMarketContextFieldProvenance | null;
  primary_focus?: OperatorAlertMarketContextFieldProvenance | null;
};

export type OperatorAlertPrimaryFocus = {
  symbol?: string | null;
  timeframe?: string | null;
  candidate_symbols: string[];
  candidate_count: number;
  policy: string;
  reason?: string | null;
};

export type OperatorAlertEntry = {
  alert_id: string;
  severity: string;
  category: string;
  summary: string;
  detail: string;
  detected_at: string;
  run_id?: string | null;
  session_id?: string | null;
  symbol?: string | null;
  symbols: string[];
  timeframe?: string | null;
  primary_focus?: OperatorAlertPrimaryFocus | null;
  occurrence_id?: string | null;
  timeline_key?: string | null;
  timeline_position?: number | null;
  timeline_total?: number | null;
  status: string;
  resolved_at?: string | null;
  source: string;
  delivery_targets: string[];
};

export type OperatorVisibility = {
  generated_at: string;
  alerts: OperatorAlertEntry[];
  alert_history: OperatorAlertEntry[];
  incident_events: {
    event_id: string;
    alert_id: string;
    timestamp: string;
    kind: string;
    severity: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    symbol?: string | null;
    symbols: string[];
    timeframe?: string | null;
    primary_focus?: OperatorAlertPrimaryFocus | null;
    source: string;
    paging_policy_id: string;
    paging_provider?: string | null;
    delivery_targets: string[];
    escalation_targets: string[];
    delivery_state: string;
    acknowledgment_state: string;
    acknowledged_at?: string | null;
    acknowledged_by?: string | null;
    acknowledgment_reason?: string | null;
    escalation_level: number;
    escalation_state: string;
    last_escalated_at?: string | null;
    last_escalated_by?: string | null;
    escalation_reason?: string | null;
    next_escalation_at?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    provider_workflow_reference?: string | null;
    external_status: string;
    external_last_synced_at?: string | null;
    paging_status: string;
    provider_workflow_state: string;
    provider_workflow_action?: string | null;
    provider_workflow_last_attempted_at?: string | null;
    remediation: {
      state: string;
      kind?: string | null;
      owner?: string | null;
      summary?: string | null;
      detail?: string | null;
      runbook?: string | null;
      requested_at?: string | null;
      requested_by?: string | null;
      last_attempted_at?: string | null;
      provider?: string | null;
      reference?: string | null;
      provider_payload: Record<string, unknown>;
      provider_payload_updated_at?: string | null;
      provider_recovery: {
        lifecycle_state: string;
        provider?: string | null;
        job_id?: string | null;
        reference?: string | null;
        workflow_reference?: string | null;
        summary?: string | null;
        detail?: string | null;
        channels: string[];
        symbols: string[];
        timeframe?: string | null;
        market_context_provenance?: OperatorAlertMarketContextProvenance | null;
        updated_at?: string | null;
        verification: {
          state: string;
          checked_at?: string | null;
          summary?: string | null;
          issues: string[];
        };
        telemetry: {
          source: string;
          state: string;
          progress_percent?: number | null;
          attempt_count: number;
          current_step?: string | null;
          last_message?: string | null;
          last_error?: string | null;
          external_run_id?: string | null;
          job_url?: string | null;
          started_at?: string | null;
          finished_at?: string | null;
          updated_at?: string | null;
        };
        status_machine: {
          state: string;
          workflow_state: string;
          workflow_action?: string | null;
          job_state: string;
          sync_state: string;
          last_event_kind?: string | null;
          last_event_at?: string | null;
          last_detail?: string | null;
          attempt_number: number;
        };
        provider_schema_kind?: string | null;
        pagerduty: {
          incident_id?: string | null;
          incident_key?: string | null;
          incident_status: string;
          urgency?: string | null;
          service_id?: string | null;
          service_summary?: string | null;
          escalation_policy_id?: string | null;
          escalation_policy_summary?: string | null;
          html_url?: string | null;
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
          acknowledged?: boolean | null;
          seen?: boolean | null;
          tiny_id?: string | null;
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
      };
    };
  }[];
  delivery_history: {
    delivery_id: string;
    incident_event_id: string;
    alert_id: string;
    incident_kind: string;
    target: string;
    status: string;
    attempted_at: string;
    detail: string;
    attempt_number: number;
    next_retry_at?: string | null;
    phase: string;
    provider_action?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    source: string;
  }[];
  audit_events: {
    event_id: string;
    timestamp: string;
    actor: string;
    kind: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    source: string;
  }[];
};

export type GuardedLiveStatus = {
  generated_at: string;
  candidacy_status: string;
  blockers: string[];
  active_alerts: OperatorAlertEntry[];
  alert_history: OperatorAlertEntry[];
  incident_events: {
    event_id: string;
    alert_id: string;
    timestamp: string;
    kind: string;
    severity: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    symbol?: string | null;
    symbols: string[];
    timeframe?: string | null;
    primary_focus?: OperatorAlertPrimaryFocus | null;
    source: string;
    paging_policy_id: string;
    paging_provider?: string | null;
    delivery_targets: string[];
    escalation_targets: string[];
    delivery_state: string;
    acknowledgment_state: string;
    acknowledged_at?: string | null;
    acknowledged_by?: string | null;
    acknowledgment_reason?: string | null;
    escalation_level: number;
    escalation_state: string;
    last_escalated_at?: string | null;
    last_escalated_by?: string | null;
    escalation_reason?: string | null;
    next_escalation_at?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    provider_workflow_reference?: string | null;
    external_status: string;
    external_last_synced_at?: string | null;
    paging_status: string;
    provider_workflow_state: string;
    provider_workflow_action?: string | null;
    provider_workflow_last_attempted_at?: string | null;
    remediation: {
      state: string;
      kind?: string | null;
      owner?: string | null;
      summary?: string | null;
      detail?: string | null;
      runbook?: string | null;
      requested_at?: string | null;
      requested_by?: string | null;
      last_attempted_at?: string | null;
      provider?: string | null;
      reference?: string | null;
      provider_payload: Record<string, unknown>;
      provider_payload_updated_at?: string | null;
      provider_recovery: {
        lifecycle_state: string;
        provider?: string | null;
        job_id?: string | null;
        reference?: string | null;
        workflow_reference?: string | null;
        summary?: string | null;
        detail?: string | null;
        channels: string[];
        symbols: string[];
        timeframe?: string | null;
        updated_at?: string | null;
        verification: {
          state: string;
          checked_at?: string | null;
          summary?: string | null;
          issues: string[];
        };
        telemetry: {
          source: string;
          state: string;
          progress_percent?: number | null;
          attempt_count: number;
          current_step?: string | null;
          last_message?: string | null;
          last_error?: string | null;
          external_run_id?: string | null;
          job_url?: string | null;
          started_at?: string | null;
          finished_at?: string | null;
          updated_at?: string | null;
        };
        status_machine: {
          state: string;
          workflow_state: string;
          workflow_action?: string | null;
          job_state: string;
          sync_state: string;
          last_event_kind?: string | null;
          last_event_at?: string | null;
          last_detail?: string | null;
          attempt_number: number;
        };
        provider_schema_kind?: string | null;
        pagerduty: {
          incident_id?: string | null;
          incident_key?: string | null;
          incident_status: string;
          urgency?: string | null;
          service_id?: string | null;
          service_summary?: string | null;
          escalation_policy_id?: string | null;
          escalation_policy_summary?: string | null;
          html_url?: string | null;
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
          acknowledged?: boolean | null;
          seen?: boolean | null;
          tiny_id?: string | null;
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
      };
    };
  }[];
  delivery_history: {
    delivery_id: string;
    incident_event_id: string;
    alert_id: string;
    incident_kind: string;
    target: string;
    status: string;
    attempted_at: string;
    detail: string;
    attempt_number: number;
    next_retry_at?: string | null;
    phase: string;
    provider_action?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    source: string;
  }[];
  kill_switch: {
    state: string;
    reason: string;
    updated_at: string;
    updated_by: string;
    activation_count: number;
    last_engaged_at?: string | null;
    last_released_at?: string | null;
  };
  reconciliation: {
    state: string;
    checked_at?: string | null;
    checked_by?: string | null;
    scope: string;
    summary: string;
    findings: {
      kind: string;
      severity: string;
      summary: string;
      detail: string;
    }[];
    internal_snapshot?: {
      captured_at: string;
      running_run_ids: string[];
      exposures: {
        run_id: string;
        mode: string;
        instrument_id: string;
        quantity: number;
      }[];
      open_order_count: number;
    } | null;
    venue_snapshot?: {
      provider: string;
      venue: string;
      verification_state: string;
      captured_at?: string | null;
      balances: {
        asset: string;
        total: number;
        free?: number | null;
        used?: number | null;
      }[];
      open_orders: {
        order_id: string;
        symbol: string;
        side: string;
        amount: number;
        status: string;
        price?: number | null;
      }[];
      issues: string[];
    } | null;
  };
  recovery: {
    state: string;
    recovered_at?: string | null;
    recovered_by?: string | null;
    reason?: string | null;
    source_snapshot_at?: string | null;
    source_verification_state: string;
    summary: string;
    exposures: {
      instrument_id: string;
      symbol: string;
      asset: string;
      quantity: number;
    }[];
    open_orders: {
      order_id: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      price?: number | null;
    }[];
    issues: string[];
  };
  ownership: {
    state: string;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    symbol?: string | null;
    claimed_at?: string | null;
    claimed_by?: string | null;
    last_heartbeat_at?: string | null;
    last_order_sync_at?: string | null;
    last_resumed_at?: string | null;
    last_reason?: string | null;
    last_released_at?: string | null;
  };
  order_book: {
    state: string;
    synced_at?: string | null;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    symbol?: string | null;
    open_orders: {
      order_id: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      price?: number | null;
    }[];
    issues: string[];
  };
  session_restore: {
    state: string;
    restored_at?: string | null;
    source: string;
    venue?: string | null;
    symbol?: string | null;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    open_orders: {
      order_id: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      price?: number | null;
    }[];
    synced_orders: {
      order_id: string;
      venue: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      submitted_at: string;
      updated_at?: string | null;
      requested_price?: number | null;
      average_fill_price?: number | null;
      fee_paid?: number | null;
      requested_amount?: number | null;
      filled_amount?: number | null;
      remaining_amount?: number | null;
      issues: string[];
    }[];
    issues: string[];
  };
  session_handoff: {
    state: string;
    handed_off_at?: string | null;
    released_at?: string | null;
    source: string;
    venue?: string | null;
    symbol?: string | null;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    venue_session_id?: string | null;
    transport: string;
    cursor?: string | null;
    last_event_at?: string | null;
    last_sync_at?: string | null;
    supervision_state: string;
    failover_count: number;
    last_failover_at?: string | null;
    coverage: string[];
    order_book_state: string;
    order_book_last_update_id?: number | null;
    order_book_gap_count: number;
    order_book_rebuild_count: number;
    order_book_last_rebuilt_at?: string | null;
    order_book_bid_level_count: number;
    order_book_ask_level_count: number;
    order_book_best_bid_price?: number | null;
    order_book_best_bid_quantity?: number | null;
    order_book_best_ask_price?: number | null;
    order_book_best_ask_quantity?: number | null;
    order_book_bids: {
      price: number;
      quantity: number;
    }[];
    order_book_asks: {
      price: number;
      quantity: number;
    }[];
    channel_restore_state: string;
    channel_restore_count: number;
    channel_last_restored_at?: string | null;
    channel_continuation_state: string;
    channel_continuation_count: number;
    channel_last_continued_at?: string | null;
    trade_snapshot?: {
      event_id?: string | null;
      price?: number | null;
      quantity?: number | null;
      event_at?: string | null;
    } | null;
    aggregate_trade_snapshot?: {
      event_id?: string | null;
      price?: number | null;
      quantity?: number | null;
      event_at?: string | null;
    } | null;
    book_ticker_snapshot?: {
      bid_price?: number | null;
      bid_quantity?: number | null;
      ask_price?: number | null;
      ask_quantity?: number | null;
      event_at?: string | null;
    } | null;
    mini_ticker_snapshot?: {
      open_price?: number | null;
      close_price?: number | null;
      high_price?: number | null;
      low_price?: number | null;
      base_volume?: number | null;
      quote_volume?: number | null;
      event_at?: string | null;
    } | null;
    kline_snapshot?: {
      timeframe?: string | null;
      open_at?: string | null;
      close_at?: string | null;
      open_price?: number | null;
      high_price?: number | null;
      low_price?: number | null;
      close_price?: number | null;
      volume?: number | null;
      closed: boolean;
      event_at?: string | null;
    } | null;
    last_market_event_at?: string | null;
    last_depth_event_at?: string | null;
    last_kline_event_at?: string | null;
    last_aggregate_trade_event_at?: string | null;
    last_mini_ticker_event_at?: string | null;
    last_account_event_at?: string | null;
    last_balance_event_at?: string | null;
    last_order_list_event_at?: string | null;
    last_trade_event_at?: string | null;
    last_book_ticker_event_at?: string | null;
    active_order_count: number;
    issues: string[];
  };
  audit_events: {
    event_id: string;
    timestamp: string;
    actor: string;
    kind: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    source: string;
  }[];
  active_runtime_alert_count: number;
  running_sandbox_count: number;
  running_paper_count: number;
  running_live_count: number;
};
