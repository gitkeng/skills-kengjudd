# Mermaid syntax rules

Load this in every phase that writes a Mermaid block. Diagrams are produced in
four phases — architecture, behavior, reference-analysis, and
operations-diagrams — and these rules apply identically in all of them.

A Mermaid parse error blanks the **entire block** and renders an error box in
its place: one bad line loses the whole diagram, not one edge. The shipped lint
(`scripts/validate_output.py`) catches the common fatal mistakes, but it is a
heuristic, not a parser — passing it is necessary, not sufficient.

Use Mermaid v11 fenced blocks and stable, readable node ids. The first nonblank
token is a valid v11 diagram type. Balance `[]`, `()`, and `{}` outside quoted
labels. Quote labels containing punctuation. Keep one diagram purpose per block
and do not use ASCII art as a substitute.

## Fatal and easy to get wrong

- **A shape belongs to a node id.** `[( )]`, `[[ ]]`, `(( ))`, `{ }` and friends
  attach to an id; there is no anonymous node. Write
  `docugent --> mongo[("MongoDB")]`, never `docugent -->[("MongoDB")]`. A shape
  token straight after an arrow is a parse error, with or without a space.
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
  you get. Inside a quoted *flowchart* label such as `a["foo; bar"]`, `;` is
  safe.
- **Close every block.** Each `subgraph` (flowchart) and each
  `loop`/`alt`/`opt`/`par`/`critical`/`rect`/`break`/`box` (sequence) needs its
  own `end`.
- **Edge labels come in pipe pairs:** `a -->|"label"| b`.
- **Flowchart direction** is one of `TB`, `TD`, `BT`, `RL`, `LR`.

## Node ids

Choose ids that are not keywords of any diagram type. `end` is the classic trap;
also avoid `actor`, `participant`, `loop`, `graph`, `subgraph`, and `class`.
Prefer descriptive ids such as `client`, `externalUser`, `perPage`, `orderStore`.

An id may be reused across blocks but must be unique within one block; two
declarations of the same id merge into one node, which silently changes the
diagram's meaning rather than failing.

## Renderer compatibility

Prefer standard `flowchart`, `sequenceDiagram`, `stateDiagram-v2`, `classDiagram`,
and `erDiagram` syntax for broad renderer support. Use Mermaid C4 directives
(`C4Context`, `C4Container`, `C4Component`) only when the available v11 renderer
supports them. `<br/>` inside a quoted label is valid and portable.
