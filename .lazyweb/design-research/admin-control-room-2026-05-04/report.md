# Quant Admin UI Research

Date: 2026-05-04

## Current State

Lazyweb MCP was confirmed healthy on 2026-05-05 and used for the quant-focused iteration. Screenshot browse tooling is not exposed in this Codex environment, so visual references are documented from Lazyweb metadata and vision descriptions rather than downloaded screenshots. The current implementation was inspected from `apps/web/src/app/WorkspaceShell.tsx`, `apps/web/src/styles.css`, and route composition under `apps/web/src/routes`.

The current admin web is a React/Vite quant operations surface with tabs, KPI cards, a workspace intro panel, and many dense operational panels. The main opportunity is to make it feel like a stock/crypto strategy operations console: clearer product language, stronger hierarchy, denser market tables, and more consistent controls.

## Research Inputs

- Lazyweb MCP search on 2026-05-05 for quant trading, stock backtesting, crypto analytics, portfolio risk, and market table screens.
- Web research on 2026 SaaS/admin dashboard UX patterns.
- Current code inspection for shell, navigation, metrics, tables, forms, route panels, and responsive behavior.
- Lazyweb MCP was unavailable in the first pass, then confirmed healthy and used for the quant-focused iteration.

## Lazyweb References Used

- Yahoo Finance compare: side-by-side stock metric comparison with valuation, performance, cash flow, return, ownership, market mover sidebar, and comparison toggles.
- AlgoTest backtest: strategy backtesting dashboard with performance metrics, reports, downloads, and FAQ/context panels.
- Harmoney: dark fixed-income risk dashboard with VaR/CVaR scenario tables and what-if simulation panels.
- Yahoo Finance crypto market: sortable coin table with price, 24h/7d change, market cap, volume, sparklines, alerts, and news feed.
- AlgoTest simulator: trading dashboard with positions, P&L tables, trade details, and performance charts.
- Webull paper trading: paper trading surface emphasizing charts, practice execution, and portfolio views.

## Direction

1. Favor command-center information density over marketing-style hero composition.
2. Present Akra Trader as a stock/crypto quant admin product, not a generic ops console.
3. Keep persistent navigation, but label it around backtesting, market data, paper trading, and guarded live execution.
4. Put status, data source, and metric context near the top so operators do not hunt for runtime health.
5. Use calmer color tokens with purposeful accent colors for strategy research, runtime, live, and risk states.
6. Improve form, table, card, and button consistency globally without rewriting generated control-room panels.

## Applied UI Principles

- Dashboard design should follow the operator's next action after reading a metric, not only display numbers.
- Admin panels need table/list density, persistent filters, visible status hierarchy, and progressive disclosure for deep controls.
- Enterprise tools should avoid decorative excess; high contrast, clear spacing, sticky navigation, and consistent controls matter more than novelty.

## Implementation Notes

- Keep the existing workspace model and route structure.
- Redesign only the shell and global CSS tokens so the large generated control-room surface receives the upgrade without broad behavioral risk.
- Convert awkward mixed English/Korean product copy into Korean-first quant admin wording, while keeping accepted finance terms like API, Equity, Crypto, Backtest, and Risk where concise.

## References

- SaaS Dashboard Design UX, Merveilleux Design, 2026-02-19.
- Dashboard Design Best Practices, Boundev, 2026-03-09.
- SaaS Dashboard UI/UX Best Practices, Octet Design, 2026-01-06.
- UX Clarity in SaaS Dashboards, Typenorm, 2026-02-03.
