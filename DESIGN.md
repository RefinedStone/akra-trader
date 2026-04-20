# Akra Trader Control Room

## Visual Theme & Atmosphere

- Operator-first trading workstation, not a marketing landing page.
- Inspired by the confidence of Coinbase and the disciplined information architecture of Linear as surfaced through `awesome-design-md` / `getdesign.md`.
- The product should feel calm, high-trust, and dense without becoming chaotic.
- Dark charcoal surfaces and cobalt accents are the base. Amber and ember are reserved for warnings, risk, and actions that deserve attention.
- The interface should reward fast scanning. Large surfaces are acceptable only when they are grouped by task and given a clear heading.

## Product Layout Rules

- The control room must be segmented into workspaces:
  - `Overview`
  - `Research`
  - `Runtime Ops`
  - `Guarded Live`
- Do not put the full product on one endless page.
- Each workspace should expose one clear purpose and only the panels needed for that purpose.
- Navigation between workspaces should stay visible while scrolling.
- Primary status should appear high on the page in compact summary cards before any detailed tables.

## Color Palette & Roles

- App background: `#07111a`
- Elevated background: `#0c1824`
- Primary panel: `rgba(12, 20, 31, 0.9)`
- Strong panel: `rgba(16, 27, 40, 0.96)`
- Border: `rgba(130, 160, 194, 0.16)`
- Strong border: `rgba(115, 149, 205, 0.28)`
- Primary text: `#f5f7fb`
- Secondary text: `#90a1b5`
- Accent blue: `#4f80ff`
- Accent cyan: `#78d4ff`
- Success: `#5ad7a4`
- Warning: `#f6b94f`
- Danger: `#ff8d7a`

## Typography

- Use a clean, modern sans with low drama for primary UI copy.
- Headings should feel crisp and slightly compressed, but not playful.
- Monospace is for metadata, system labels, timestamps, and identifiers only.
- Heading hierarchy should be obvious:
  - Page title: strong and direct
  - Workspace title: prominent but smaller than the page title
  - Panel title: compact and functional

## Components

### Hero

- Short and functional.
- Explain the product in one clear sentence.
- The hero should include live status context, not decorative filler.

### Workspace Navigation

- Use large segmented navigation cards or tabs.
- Each workspace item should communicate:
  - name
  - purpose
  - current state summary
- Active workspace should be obvious through border, background, and accent treatment.

### Summary Cards

- Put core metrics in compact cards near the top.
- Each card should expose:
  - label
  - one strong value
  - one short supporting detail
- Do not overload cards with mini tables.

### Panels

- Panels should look deliberate and modular.
- Wide panels are allowed for data tables and run-history surfaces.
- Avoid stacking too many wide panels in a single workspace when the surrounding context is unrelated.

### Buttons

- Primary actions should use blue emphasis.
- Secondary actions should be subdued ghost buttons.
- Dangerous or high-risk actions should not look identical to routine actions.

## Content Density Rules

- Dense data is acceptable inside runtime and live panels.
- Density must come from structure, not from dumping every surface into one scroll.
- Always separate:
  - research actions
  - runtime monitoring
  - guarded-live intervention
- If a panel exists mainly for reference, it should live behind the workspace where it is used.

## Motion & Interaction

- Use restrained transitions for hover, focus, and active state changes.
- Prefer subtle elevation and border changes over flashy animation.
- Sticky navigation is encouraged when it improves orientation.

## Do

- Keep the experience task-based.
- Use strong headings and short supporting copy.
- Make risk states visually distinct.
- Give operators a fast path to the next relevant workspace.
- Preserve data density where the domain requires it.

## Do Not

- Do not recreate a long single-page dashboard.
- Do not use accent colors as decoration without meaning.
- Do not mix research and live controls in the same visual block.
- Do not let giant tables become the only navigation mechanism.
- Do not introduce purple-heavy branding or generic SaaS gradients.

## Responsive Behavior

- Desktop should use multi-column panel layouts.
- Tablet and mobile should collapse to single-column or two-column navigation without losing workspace segmentation.
- Sticky workspace navigation can relax on smaller screens if it impedes content.

## Agent Prompt Guide

- When editing this frontend, optimize first for operator clarity and reduced scroll depth.
- Preserve the existing domain surfaces, but reorganize them into cleaner workspaces instead of removing capability.
- Prefer a restrained fintech control-room aesthetic over decorative dashboard patterns.
