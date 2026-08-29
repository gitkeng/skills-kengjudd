# Diagram playbook

Mermaid source: https://mermaid.js.org/. Use Mermaid v11 fenced blocks and stable, readable node IDs. Every diagram statement is backed by source evidence in nearby prose or an evidence table.

## Structural

`diagrams/structural/component-diagrams.md` contains at least one component diagram and one class or package/module diagram. Show components, ownership, direction, interfaces, and important data stores; avoid implying deployment identity from namespaces alone.

## Behavioral

`diagrams/behavioral/sequence-diagrams.md` contains at least two `sequenceDiagram` blocks for key user/system flows plus at least one `stateDiagram-v2` or activity-style `flowchart` for an entity lifecycle. Include alternate/error paths and anchor each flow to code entry points.

## Architecture

`diagrams/architecture/system-context.md` contains a system-context view with actors, external systems, deployment boundary, trust boundaries, protocols, and data direction. Prefer standard Mermaid flowchart syntax for broad renderer compatibility; use Mermaid C4 directives only when the available v11 renderer supports them.

## Syntax discipline

The first nonblank token is a valid v11 diagram type. Balance `[]`, `()`, and `{}` outside quoted labels. Quote labels containing punctuation. Keep one diagram purpose per block and do not use ASCII art as a substitute.
