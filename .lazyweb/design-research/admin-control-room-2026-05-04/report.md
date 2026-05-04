# Admin Control Room UI Research

Date: 2026-05-04

## Current State

Lazyweb MCP and screenshot browse tooling are not exposed in this Codex environment, so no Lazyweb database screenshots could be downloaded. The current implementation was inspected from `apps/web/src/app/WorkspaceShell.tsx`, `apps/web/src/styles.css`, and route composition under `apps/web/src/routes`.

The current admin web is a React/Vite control room with workspace tabs, KPI cards, a workspace intro panel, and many dense operational panels. The main opportunity is to make it feel like an operations console: stronger hierarchy, less decorative hero treatment, denser status reading, and more consistent controls.

## Research Inputs

- Web research on 2026 SaaS/admin dashboard UX patterns.
- Current code inspection for shell, navigation, metrics, tables, forms, route panels, and responsive behavior.
- Lazyweb skill attempted; MCP and browse tools unavailable in this session, so implementation used web research plus local artifact inspection.

## Direction

1. Favor command-center information density over marketing-style hero composition.
2. Keep persistent workspace navigation, but make it scan like operational tabs with clear active state.
3. Put status and API context near the top so operators do not hunt for runtime health.
4. Use calmer color tokens with purposeful accent colors for research/runtime/live/warning states.
5. Improve form, table, card, and button consistency globally without rewriting generated control-room panels.

## Applied UI Principles

- Dashboard design should follow the operator's next action after reading a metric, not only display numbers.
- Admin panels need table/list density, persistent filters, visible status hierarchy, and progressive disclosure for deep controls.
- Enterprise tools should avoid decorative excess; high contrast, clear spacing, sticky navigation, and consistent controls matter more than novelty.

## Implementation Notes

- Keep the existing workspace model and route structure.
- Redesign only the shell and global CSS tokens so the large generated control-room surface receives the upgrade without broad behavioral risk.
- Preserve Korean operational copy where it communicates workflow intent, while making the primary headline shorter and more scannable.

## References

- SaaS Dashboard Design UX, Merveilleux Design, 2026-02-19.
- Dashboard Design Best Practices, Boundev, 2026-03-09.
- SaaS Dashboard UI/UX Best Practices, Octet Design, 2026-01-06.
- UX Clarity in SaaS Dashboards, Typenorm, 2026-02-03.
