# Operator Delivery Matrix

Updated for the repository state as of April 21, 2026.

This document summarizes the operator-delivery surface without repeating a long provider list in
every product-facing document.

## Current Posture

The operator-delivery layer already supports:

- local and simple destinations such as console logging, generic webhooks, and Slack webhooks
- broad incident-management and on-call provider fanout
- persisted delivery-attempt history, retry timing, acknowledgment, escalation, and remediation state
- callback and pull-sync based workflow reconciliation for supported providers

This is a meaningful safety and visibility substrate, but it is not yet a replacement for a full
provider-owned incident-management system.

## Destination Families

| Family | Current posture | Examples |
| --- | --- | --- |
| Local and generic | solid baseline | console, generic webhook, Slack webhook |
| Incident and on-call | broad provider coverage | PagerDuty, incident.io, FireHydrant, Rootly, Blameless, xMatters, ServiceNow, Squadcast, BigPanda, Grafana OnCall, Splunk On-Call, Jira Service Management, Opsgenie, Zenduty |
| Alerting and secondary paging | broad provider coverage | PagerTree, AlertOps, SIGNL4, iLert, Better Stack, OnPage, All Quiet, Moogsoft, Spike.sh, DutyCalls, IncidentHub, Resolver, OpenDuty, Cabot, HaloITSM, incidentmanager.io, OneUptime, Squzy, Crises Control |
| Service desk and helpdesk | broad provider coverage | Freshservice, Freshdesk, HappyFox, Zendesk, Zoho Desk, Help Scout, Kayako, Intercom, Front, ManageEngine ServiceDesk Plus, SysAid, BMC Helix, SolarWinds Service Desk, TOPdesk, InvGate Service Desk, OpsRamp |

## What Is Already Implemented

- delivery fanout to supported providers
- persisted delivery-attempt history with retry timing
- acknowledgment and escalation state
- remediation metadata and supported remediation workflow actions
- provider callback sync and provider pull-sync posture for supported workflows
- typed provider recovery-state branches instead of one flattened generic payload

## What Is Still Missing

- full provider-owned incident ownership semantics
- broader policy-management abstractions
- a simpler product-facing explanation of which providers are officially supported in operational use

## Source Of Truth

For the exact code-level provider list and settings surface, consult:

- `apps/api/src/akra_trader/config.py`
- `apps/api/src/akra_trader/adapters/operator_delivery.py`
