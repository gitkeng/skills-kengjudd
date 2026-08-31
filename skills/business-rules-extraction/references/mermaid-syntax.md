# Mermaid syntax rules

Load this before writing any Mermaid block. Diagrams appear in each domain's
`diagrams.md` (sequence, component, workflow/state) and wherever a workflow,
integration, or overview document illustrates a process; these rules apply
identically everywhere. Adapted from the sibling skill
`codebase-analysis`, where they were calibrated against the real
Mermaid parser.

A Mermaid parse error blanks the **entire block** and renders an error box in
its place: one bad line loses the whole diagram, not one edge. The shipped lint
(`scripts/validate_output.py`, check class 11) catches the common fatal
mistakes, but it is a heuristic, not a parser — passing it is necessary, not
sufficient.

Use Mermaid v11 fenced blocks and stable, readable node ids. The first nonblank
token is a valid v11 diagram type. Balance `[]`, `()`, and `{}` outside quoted
labels. Quote labels containing punctuation. Keep one diagram purpose per block
and do not use ASCII art as a substitute.

## Fatal and easy to get wrong

- **A shape belongs to a node id.** `[( )]`, `[[ ]]`, `(( ))`, `{ }` and friends
  attach to an id; there is no anonymous node. Write
  `orderSvc --> ledger[("Ledger store")]`, never `orderSvc -->[("Ledger store")]`.
  A shape token straight after an arrow is a parse error, with or without a space.
- **Keywords do not cross diagram types.** `actor`, `participant`, `autonumber`,
  `activate`, and `deactivate` exist only in `sequenceDiagram`. In a `flowchart`
  an actor is an ordinary node — `client["Upstream service"]` — and writing
  `actor client["…"]` is a parse error. Conversely `subgraph` is flowchart-only.
- **Never put `;` inside a `sequenceDiagram` message *or note*.** Text after `:`
  is read raw, so `;` is a statement separator: it truncates the text and orphans
  the rest of the line. Use `,`. This is fatal in all three positions —
  `a->>b: merge; skip`, `note over a,b: merge; skip`, and
  `note right of a: merge; skip` — and **quoting does not rescue any of them**:
  `a->>b: "merge; skip"` is still a parse error. The lint is silent on every one
  of these except the plain unquoted message, so this bullet is the only warning
  you get. Inside a quoted *flowchart* label such as `a["priced; then settled"]`,
  `;` is safe.
- **Close every block.** Each `subgraph` (flowchart) and each
  `loop`/`alt`/`opt`/`par`/`critical`/`rect`/`break`/`box` (sequence) needs its
  own `end`.
- **Edge labels come in pipe pairs:** `a -->|"label"| b`.
- **Flowchart direction** is one of `TB`, `TD`, `BT`, `RL`, `LR`.

## Node ids

Choose ids that are not keywords of any diagram type. `end` is the classic trap;
also avoid `actor`, `participant`, `loop`, `graph`, `subgraph`, and `class`.
Prefer descriptive, business-vocabulary ids such as `client`, `externalUser`,
`orderStore`, `pricingComponent`.

An id may be reused across blocks but must be unique within one block; two
declarations of the same id merge into one node, which silently changes the
diagram's meaning rather than failing.

## The three required per-domain diagrams

Three diagrams means three separate blocks. One `flowchart` may serve as the
component diagram *or* as the workflow diagram, never as both.

- **Sequence** — `sequenceDiagram`. Declare each side with `participant` (or
  `actor`) before the first message; keep message text free of `;`.
- **Component** — `flowchart`/`graph` (or `classDiagram`, or a C4 directive when
  the renderer supports it). Group a domain's components with
  `subgraph … end`.
- **Workflow/state** — `stateDiagram-v2` for a state machine, or a `flowchart`
  for a process flow with decision nodes.

## Renderer compatibility

Prefer standard `flowchart`, `sequenceDiagram`, `stateDiagram-v2`, `classDiagram`,
and `erDiagram` syntax for broad renderer support. Use Mermaid C4 directives
(`C4Context`, `C4Container`, `C4Component`) only when the available v11 renderer
supports them. `<br/>` inside a quoted label is valid and portable.
