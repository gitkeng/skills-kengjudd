# UX, theme, and accessibility contract

## Visual direction

A neutral, capability-first component design: restrained borders and shadows,
compact cards, semantic badges, a system-local font stack, one shared radius
scale, and a reproducible neutral palette. No product brand, logo, or copied
third-party CSS. The shipped CSS is the source of truth and is inlined into
`index.html` for `file://` portability.

## Layout

- Desktop: sticky sidebar plus a top toolbar; all sections remain in the
  document flow.
- Mobile (`<= 800px`): navigation wraps/stacks. There is no modal drawer.

## Navigation and controls

- Primary navigation uses ordinary in-page anchors with `aria-current`, not
  JS-gated tabs. JavaScript only adds scroll-spy.
- Disclosures use native `<button>`/`<summary>` elements with `aria-expanded`
  and `aria-controls`. There are no div-as-button controls. Panels render
  expanded server-side; JavaScript collapses them progressively.
- Sortable tables use named header buttons and update `aria-sort`.
- Filters have a persistent visible label and an `aria-live="polite"` result
  count.
- Every control has a non-empty text accessible name; icons are supplemental.
- Skip link, semantic landmarks (`header`, `nav`, `main`, `aside`), table
  captions, correct heading order, and visible keyboard focus are mandatory.

## Theme model

- The selector exposes **System**, **Light**, and **Dark** with text labels; it
  is never color-only.
- Initial mode: a saved valid preference if present; otherwise `system` via
  `matchMedia('(prefers-color-scheme: dark)')`.
- Explicit choices persist in `localStorage` under the versioned neutral key
  `car:theme:v1`. All storage access is wrapped in `try/catch`; a missing,
  invalid, or exception-raising read resolves to System and never blocks render.
- When set to System, the report reacts to OS theme changes via a `matchMedia`
  listener.
- An inline blocking `<head>` script sets `data-theme` and `color-scheme`
  before first paint to avoid a flash. The deferred script updates
  `aria-pressed` and an `aria-live` status label.

## Contrast (WCAG 2.1 AA, contractual in both themes)

- Body text ≥ 4.5:1; large text, interactive-control boundaries
  (`--border-strong`), and focus indicators ≥ 3:1. The decorative `--border`
  and badge-border tokens are exempt: the paired text always carries the
  information and meets 4.5:1 on its own.
- Color is never the sole severity/status cue: every badge carries its text.
- Token pairs are checked programmatically by the test suite in both themes.

## Motion and print

- `prefers-reduced-motion: reduce` removes non-essential transitions and
  animations and disables smooth scroll.
- Print forces a light, high-contrast palette, expands all disclosures, keeps
  Mermaid source visible, and hides chrome (sidebar, toolbar, theme control,
  filters, sort buttons). No report content remains `display:none` in print.
