# Diagram templates

## structural/component-diagrams.md

```mermaid
flowchart LR
  entry["Entry component"] --> core["Core component"]
  core --> data[("Owned data")]
```

```mermaid
classDiagram
  class PublicContract
  class Implementation
  PublicContract <|.. Implementation
```

## behavioral/sequence-diagrams.md

```mermaid
sequenceDiagram
  actor User
  participant Entry
  participant Core
  User->>Entry: Request
  Entry->>Core: Invoke
  Core-->>Entry: Result
  Entry-->>User: Response
```

```mermaid
sequenceDiagram
  actor Operator
  participant Trigger
  participant Worker
  Operator->>Trigger: Start
  Trigger->>Worker: Dispatch
  Worker-->>Trigger: Outcome
```

```mermaid
stateDiagram-v2
  [*] --> Created
  Created --> Active
  Active --> Closed
  Closed --> [*]
```

## architecture/system-context.md

```mermaid
flowchart LR
  externalUser["External actor"] -->|"request"| trustA["Trust boundary A"]
  trustA --> system["Analyzed system"]
  system -->|"integration"| trustB["Trust boundary B"]
```

In a flowchart an actor is an ordinary node — do not write `actor externalUser["…"]`.
`actor` is a `sequenceDiagram` keyword and is a parse error here (see the sequence
templates above for its legitimate use).

Replace placeholders with evidence-backed names. Add an evidence table after every block.
