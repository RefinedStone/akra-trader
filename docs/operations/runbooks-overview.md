# Operations

Compact single-operator checklist as of May 11, 2026.

## Daily Start

1. Check market-data freshness, gaps, backfill state, and recent sync failures.
2. Check active sandbox, paper, and guarded-live sessions.
3. Review open incidents, failed delivery attempts, unresolved acknowledgments, and remediation
   state.
4. Confirm guarded-live blockers, kill-switch state, reconciliation status, and open-order snapshots.
5. Record material operator decisions in product surfaces where possible.

## Incident Triage

- Data incident: stop promotion, inspect lineage history and ingestion jobs, export drill evidence
  when the issue can affect rerun claims or guarded-live candidacy.
- Sandbox incident: stop or hold the session when heartbeat, lag, fills, or decisions cannot be
  trusted; compare against run history before promotion.
- Guarded-live incident: prefer kill switch and reconciliation over manual continuation when venue
  state, local state, or operator intent diverges.
- Delivery incident: treat provider fanout as a visibility aid until provider-owned incident
  ownership is explicit for that destination.

## Guarded-Live Rules

- Do not launch live unless configuration, market data, reconciliation, recovery, and audit gates
  are green.
- Engage kill switch when order state, venue state, or operator intent is ambiguous.
- Release kill switch only after reconciliation confirms local and venue state are aligned.
- Keep venue-specific lifecycle gaps visible in roadmap/status docs until tested through product UX.

## Release And Docs Rule

For meaningful feature changes:

1. Update [Current State](../status/current-state.md).
2. Update [Roadmap](../roadmap/README.md) if remaining work changed.
3. Update this file if operator actions or escalation rules changed.
4. Update [Architecture](../architecture.md) if ownership boundaries changed.

## Known Operational Gaps

- deployment and backup runbooks are not product-grade
- credential rotation and secret governance are incomplete
- drill validation is not fully represented in product UX
- provider-owned incident ownership and policy management are incomplete
