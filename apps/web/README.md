# Akra Trader Web

React + TypeScript control room for `akra-trader`.

## Scope

Implemented:

- workspace shell and route-owned overview, market, research, runtime, and guarded-live sections
- strategy catalog, reference catalog, benchmark context, run launch, run history, comparison, and
  query-builder flows
- market-data health, gap, backfill, lineage, and incident views
- sandbox, paper, and guarded-live launch/control panels
- guarded-live alerts, delivery history, kill switch, reconciliation, recovery, and incidents
- split control-room API/type barrels plus feature-owned query-builder and run-history modules

Still incomplete:

- active-session-first runtime UX is not consistently simple yet
- several control-room panels remain large and need flow-level decomposition
- guarded-live and provider-provenance workflows need clearer operator affordances

## Run

```bash
npm install
npm run dev
```

The app reads `VITE_API_BASE_URL` and defaults to `http://localhost:8000/api`.
