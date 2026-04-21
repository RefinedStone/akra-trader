# Release And Docs Checklist

Purpose: keep implementation, operator guidance, and planning documents aligned whenever a
meaningful change lands.

## When To Run

- before merging or shipping a meaningful feature change
- after changing operator-visible workflows
- after changing run-surface contracts, guarded-live gates, or promotion posture

## Required Updates

1. Update `docs/status/current-state.md` when implemented capability or risk posture changed.
2. Update at least one roadmap or operations document that explains the remaining work or the new workflow.
3. Update blueprint wording only if the long-horizon gate, promise, or operating model changed.
4. Update runbooks when operator actions, blocking conditions, or escalation rules changed.

## Verification Checklist

1. Confirm README, status, roadmap, blueprint, and directions do not disagree on current progress.
2. Confirm research, sandbox, paper, and guarded-live are described as distinct modes where relevant.
3. Confirm new product-visible actions are linked to a runbook or an operator-facing explanation.
4. Confirm missing work is still described as missing rather than implied to be complete.
5. Confirm tests or verification notes are recorded when the change materially affects behavior.

## Required Follow-Up For Gaps

If a change exposes a workflow the docs cannot explain:

1. Record the gap before closing the release.
2. Add or update the relevant runbook in the same change set when feasible.
3. If full documentation is not possible immediately, mark the gap explicitly in roadmap or status docs.

## Release Gate Questions

- What changed for the operator?
- What changed for safety, lineage, or promotion decisions?
- Which document is now the source of truth for the changed behavior?
- What remains incomplete after this release?

## Related Runbooks

- [Runbooks Overview](runbooks-overview.md)
- [Daily Operations Checklist](daily-operations-checklist.md)
- [Data Incident Response](data-incident-response.md)
- [Sandbox Runtime Incident](sandbox-runtime-incident.md)
- [Guarded-Live Reconciliation Drill](guarded-live-reconciliation-drill.md)
- [Kill-Switch Procedure](kill-switch-procedure.md)
