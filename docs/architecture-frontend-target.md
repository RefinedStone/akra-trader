# Frontend Architecture Target

Updated for the refactor baseline as of April 21, 2026.

## Summary

The frontend target is a workspace-routed control room where route state, shell layout, feature API
calls, and dense presentation blocks can be understood in smaller units.

This wave introduces the first routing skeleton:

- workspace route state moved into `apps/web/src/app/useWorkspaceRoute.ts`
- workspace descriptors moved into `apps/web/src/app/workspaces.ts`
- shell/header/nav layout moved into `apps/web/src/app/WorkspaceShell.tsx`
- workspace panel grouping moved into `apps/web/src/routes/*`
- `App.tsx` now delegates active route composition to `WorkspaceRouteContent.tsx`
- shared control-room types/constants moved into `apps/web/src/controlRoomDefinitions.ts`
- transport helpers moved into `apps/web/src/controlRoomApi.ts`

The large control-room feature file still exists, but the top-level app shell is no longer the place
where routing and presentation structure are decided.

## Target Structure

- `src/app/`
  - router state
  - shell layout
  - workspace metadata
- `src/routes/`
  - route-specific entry modules for overview, research, runtime ops, and guarded live
- `src/features/`
  - run launch
  - run history
  - presets
  - comparison
  - market data
  - incidents
  - guarded-live controls
- `src/shared/`
  - API utilities
  - common types
  - reusable UI primitives

## Boundary Rules

- top-level `App.tsx` should become shell composition only.
- route selection must live outside feature rendering logic.
- feature fetch helpers should group by feature, not accumulate in one file.
- raw payload rendering must stay inside feature components, not shell layout.
- no new workspace sections should be added directly to shell markup without a route or feature owner.

## First-Wave Move Map

- workspace route state
  - move path parsing and history interaction into `useWorkspaceRoute.ts`
- workspace metadata
  - keep labels, summaries, and path mapping in `workspaces.ts`
- shell layout
  - keep hero, nav, refresh action, and workspace intro in `WorkspaceShell.tsx`
- route composition
  - keep overview, research, runtime ops, and guarded-live panel grouping in `src/routes/*`
- remaining giant feature body
  - dense feature JSX still lives mostly in `App.tsx`
  - top-level control-room type/constant and API helper context no longer lives inline in that file
  - next waves should split those panels into feature-owned modules behind each route

## Remaining Pressure Points

- `App.tsx` still owns too much feature state and JSX.
- route modules now own panel grouping, but they do not yet own their own data loading or feature-local state.
- shared types/constants and API helpers now have their own modules, but feature-local clients and
  dense rendering logic are still mixed into the control-room file.
- comparison/history tooling is still large enough to deserve its own subsystem.

## Done Criteria For This Track

- route state is independent from the control-room rendering body
- shell layout can change without touching dense feature logic
- workspace panel grouping can change without rewriting route selection branches in `App.tsx`
- new workspace-level navigation changes happen under `src/app/*`
- next feature splits can move one workspace at a time without redefining routing
