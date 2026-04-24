# Operator Lineage Guidance

Updated for the repository state as of April 24, 2026.

Purpose: define how an operator should interpret dataset-boundary claims, rerun validation
categories, lineage-history records, and ingestion-job history before using a run for comparison,
promotion, or runtime safety decisions.

This runbook defines the operational policy. The product now enforces the baseline lineage-history
and ingestion-job TTL floors through the market-data lineage evidence retention control, and it
exports product-native drill evidence packs from the same lineage and ingestion evidence.

## When To Run

- before accepting a rerun or comparison result as evidence
- before promoting a preset, strategy version, or benchmark claim
- when market-data freshness, gap windows, or ingestion failures affect an active decision
- after a data incident that changed a dataset, checkpoint, or effective market-data window
- during monthly operator drills for data-trust readiness

## Product Surfaces

- run provenance and rerun-boundary views
- run lineage summaries on run detail payloads
- market-data lineage history query surface
- market-data ingestion-job history query surface
- market-data lineage evidence retention prune control
- market-data lineage drill evidence pack export
- control-room data incident triage and focused market-data workflow panels
- preset promotion actions that can store lineage drill evidence pack IDs, retention expiry, and
  summary posture on the lifecycle event
- guarded-live incident escalation actions that can store the same pack link on the incident record
- comparison and rerun surfaces that expose validation category and summary

## Lineage Postures

Use these postures when deciding whether a run can support a claim:

| Input | Operator posture | Allowed use |
| --- | --- | --- |
| `validation_claim=exact_dataset` | exact-match | exact rerun, benchmark, and promotion evidence for the recorded dataset boundary |
| `validation_claim=checkpoint_window` | exact-match | checkpoint-based rerun and benchmark evidence when exact candle digests are unavailable |
| `validation_claim=window_only` | drift-aware | research comparison only; do not claim identical replay |
| `validation_claim=delegated` | drift-aware | benchmark context only until the external runtime can prove the dataset boundary |
| missing or unknown boundary | unresolved | block promotion and rerun acceptance until the boundary is explicit |

Treat `exact-match` as evidence only for the recorded boundary. It is not evidence for a different
symbol set, timeframe, strategy version, parameter set, fee model, slippage model, or execution
mode.

## Rerun Validation Categories

Use the category from run provenance when a rerun exists:

| Category | Operator action |
| --- | --- |
| `exact_match` | Accept as exact rerun evidence for the stored boundary. |
| `checkpoint_match` | Accept as checkpoint-anchored evidence; record that candle-level digest evidence was not present. |
| `window_match` | Review as drift-aware only; do not use for identical replay or promotion claims. |
| `delegated_match` | Review as drift-aware unless the external runtime evidence is attached. |
| `mode_translation` | Compare behavior as an expected mode translation, not as an identical rerun. |
| `dataset_changed` | Block promotion; rerun or resync against the intended dataset identity. |
| `checkpoint_changed` | Block promotion; rerun against the intended checkpoint or re-establish the checkpoint boundary. |
| `window_changed` | Block comparison claims until requested and effective windows match the source boundary. |
| `validation_downgrade` | Block promotion until the rerun regains the source boundary claim. |
| `validation_claim_changed` | Block promotion until source and target share one boundary claim. |
| `execution_contract_changed` | Block rerun acceptance until mode, cash, fees, slippage, strategy version, and resolved params match. |
| `boundary_mismatch` | Block and inspect lineage details before continuing. |
| `source_boundary_unavailable` | Block until the source run exposes a dataset-boundary contract. |
| `target_boundary_unavailable` | Block until the rerun exposes a dataset-boundary contract. |

If the product summary says `blocking=true`, the operator must not turn that run into promotion,
benchmark, or guarded-live readiness evidence.

## Retention Policy

The minimum retention policy for lineage review is:

| Evidence | Minimum retention |
| --- | --- |
| run provenance, dataset-boundary contract, rerun boundary, validation category | lifetime of the run record |
| market-data lineage history used by promotion, benchmark, or incident closeout | 180 days, or lifetime of the linked promotion/incident record if longer |
| market-data lineage history not linked to a decision | 90 days |
| ingestion-job history linked to a failed sync, gap, or incident | 90 days after incident closeout |
| ingestion-job history not linked to an incident | 30 days |
| exported drill evidence pack | 180 days |
| guarded-live-affecting lineage evidence | 1 year, or the live audit retention period if longer |

The product TTL control clamps requested retention windows up to these floors before pruning
lineage-history or ingestion-job records. Manual cleanup outside that control must preserve the
same minimum evidence. Do not prune the only record that explains why a run was accepted, blocked,
or escalated.

## Workflow Links

When a promotion or guarded-live escalation depends on lineage evidence, generate the product-native
drill evidence pack from the focused market-data workflow before completing the action. The control
room stores the pack ID, retention expiry, and summary posture on promoted preset lifecycle events
and escalated guarded-live incidents so later reviews can open the same evidence trail without
reconstructing it from raw lineage tables.

If the product cannot resolve an affected symbol and timeframe for a drill evidence pack, complete
the operator action only when the reason text explains why the evidence link is missing.

## Escalation Rules

Escalate a lineage issue when any of the following are true:

- a guarded-live, paper, or sandbox decision depends on stale or ambiguous data
- a promotion candidate has `blocking=true` or any drift category that is not explicitly accepted
  as drift-aware research
- the same venue, symbol set, or timeframe produces repeated ingestion failures across two sync
  cycles
- the operator cannot identify the dataset identity, checkpoint, or effective window used for the
  decision
- a delegated runtime is the only source of proof and external boundary evidence is missing

Escalation output must include the affected venue, symbols, timeframe, run IDs, boundary IDs if
present, validation claim, validation category, and the operator decision being blocked.

## Drill Validation Pack

Run this pack monthly, after lineage-related code changes, and before relying on a new venue or
runtime lane for promotion evidence.

### Scenario A: Exact Dataset Match

1. Select a run with `validation_claim=exact_dataset`.
2. Rerun from its stored boundary with the same strategy, params, mode, fees, slippage, symbols,
   and timeframe.
3. Confirm the rerun category is `exact_match`.
4. Record the source run ID, rerun ID, dataset identity, rerun boundary ID, and operator decision.

Expected result: the run can support exact rerun and benchmark claims for that boundary.

### Scenario B: Checkpoint-Anchored Match

1. Select or construct a run with `validation_claim=checkpoint_window`.
2. Rerun from the stored checkpoint boundary.
3. Confirm the rerun category is `checkpoint_match`.
4. Record that candle-level dataset identity is not available.

Expected result: the run can support checkpoint-based claims, but the closeout must not describe it
as candle-digest exact.

### Scenario C: Drift-Aware Boundary

1. Select a `window_only` or `delegated` run.
2. Confirm the lineage summary returns a review posture rather than clear exact-match evidence.
3. Attempt to use it as promotion evidence only in the drill notes, not in production records.
4. Record the blocking reason that would prevent identical replay claims.

Expected result: the operator can explain why this is research context, not exact evidence.

### Scenario D: Drift Or Contract Mismatch

1. Compare source and rerun records with changed dataset identity, checkpoint, window, validation
   claim, mode, strategy version, fees, slippage, or resolved params.
2. Confirm the validation category identifies the mismatch instead of collapsing into generic drift.
3. Confirm the operator summary blocks promotion when the mismatch affects evidence quality.

Expected result: the run is blocked until the intended boundary or execution contract is restored.

### Scenario E: Ingestion Incident Closeout

1. Pick a stale-data, sync-failure, or gap-expansion incident.
2. Query lineage history and ingestion-job history for the affected venue, symbol set, and timeframe.
3. Confirm the closeout identifies final posture as exact-match, drift-aware, or unresolved.
4. Confirm the evidence is retained under the policy above.

Expected result: the incident can be reopened later without reconstructing the decision from raw
logs.

## Evidence Pack Template

Record the following in the drill or incident closeout:

- date and operator
- scenario or incident identifier
- affected venue, symbols, and timeframe
- source run ID and rerun ID, when applicable
- dataset identity, sync checkpoint ID, and rerun boundary ID, when present
- validation claim and rerun validation category
- lineage-history query filters used
- ingestion-job query filters used
- product export pack ID and retention expiration, when generated
- final posture: exact-match, drift-aware, or unresolved
- operator decision: accepted, reviewed, blocked, or escalated
- linked incident, export, or delivery artifact, when present

## Closeout Rules

- `exact-match` closeout must name the boundary that was accepted.
- `drift-aware` closeout must state which claim is intentionally weaker and what use is still
  allowed.
- `unresolved` closeout must leave the affected promotion, benchmark, or runtime decision blocked.
- Any guarded-live-affecting lineage ambiguity must stay escalated until reconciliation and data
  posture are both clear.

## Related Runbooks

- [Data Incident Response](data-incident-response.md)
- [Daily Operations Checklist](daily-operations-checklist.md)
- [Guarded-Live Reconciliation Drill](guarded-live-reconciliation-drill.md)
- [Release And Docs Checklist](release-and-docs-checklist.md)
