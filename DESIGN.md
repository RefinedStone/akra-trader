# ▲ 111,956,000 BTC/KRW +1.76%

## Mission
Create implementation-ready, token-driven UI guidance for ▲ 111,956,000 BTC/KRW +1.76% that is optimized for consistency, accessibility, and fast delivery across dashboard web app.

## Brand
- Product/brand: ▲ 111,956,000 BTC/KRW +1.76%
- URL: https://www.upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC
- Audience: authenticated users and operators
- Product surface: dashboard web app

## Style Foundations
- Visual style: clean, functional, implementation-oriented
- Main font style: `font.family.primary=Roboto`, `font.family.stack=Roboto, Noto Sans KR, sans-serif, AppleSDGothicNeo-Regular, Malgun Gothic, Dotum, sans-serif`, `font.size.base=12px`, `font.weight.base=400`, `font.lineHeight.base=normal`
- Typography scale: `font.size.xs=11px`, `font.size.sm=12px`, `font.size.md=14px`, `font.size.lg=15px`, `font.size.xl=16px`, `font.size.2xl=34px`
- Color palette: `color.text.primary=#333333`, `color.text.secondary=#dd3c44`, `color.text.tertiary=#0062df`, `color.text.inverse=#1375ec`, `color.surface.base=#000000`, `color.surface.muted=#e9ecf1`, `color.surface.raised=#edeef1`
- Spacing scale: `space.1=2px`, `space.2=4px`, `space.3=6px`, `space.4=8px`, `space.5=9px`, `space.6=10px`, `space.7=16px`, `space.8=17px`
- Radius/shadow/motion tokens: `radius.xs=4px`

## Dashboard Structure
- The control room must stay segmented into `Overview`, `Research`, `Runtime Ops`, and `Guarded Live`.
- Each workspace must expose summary metrics first and detailed operational content second.
- Long operational detail should default to collapsed disclosure panels instead of open full-page stacks.
- Dense data is allowed, but it must stay inside clearly bordered cards or disclosures with visible headings.
- Workspace navigation should remain visible and should clearly show the active surface.

## Readability Rules
- Long identifiers, payloads, and status copy must wrap without overflowing their container.
- Body copy should use the primary font stack. Monospace should be limited to timestamps, IDs, and compact metadata.
- Large tables should prefer compact density, but they must remain readable on smaller widths.
- Metric tiles and cards should expose a short label, one primary value, and one supporting line only.
- Interactive controls should preserve visible borders on light surfaces.

## Accessibility
- Target: WCAG 2.2 AA
- Keyboard-first interactions required.
- Focus-visible rules required.
- Contrast constraints required.

## Writing Tone
Concise, confident, implementation-focused.

## Rules: Do
- Use semantic tokens, not raw hex values, in component guidance.
- Every component must define states for default, hover, focus-visible, active, disabled, loading, and error.
- Component behavior should specify responsive and edge-case handling.
- Interactive components must document keyboard, pointer, and touch behavior.
- Accessibility acceptance criteria must be testable in implementation.

## Rules: Don't
- Do not allow low-contrast text or hidden focus indicators.
- Do not introduce one-off spacing or typography exceptions.
- Do not use ambiguous labels or non-descriptive actions.
- Do not ship component guidance without explicit state rules.

## Guideline Authoring Workflow
1. Restate design intent in one sentence.
2. Define foundations and semantic tokens.
3. Define component anatomy, variants, interactions, and state behavior.
4. Add accessibility acceptance criteria with pass/fail checks.
5. Add anti-patterns, migration notes, and edge-case handling.
6. End with a QA checklist.

## Required Output Structure
- Context and goals.
- Design tokens and foundations.
- Component-level rules (anatomy, variants, states, responsive behavior).
- Accessibility requirements and testable acceptance criteria.
- Content and tone standards with examples.
- Anti-patterns and prohibited implementations.
- QA checklist.

## Component Rule Expectations
- Include keyboard, pointer, and touch behavior.
- Include spacing and typography token requirements.
- Include long-content, overflow, and empty-state handling.
- Include known page component density: links (298), tables (37), buttons (16), lists (15), inputs (7), cards (6), navigation (3).


## Quality Gates
- Every non-negotiable rule must use "must".
- Every recommendation should use "should".
- Every accessibility rule must be testable in implementation.
- Teams should prefer system consistency over local visual exceptions.
