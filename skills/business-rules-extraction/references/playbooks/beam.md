# BEAM Playbook — Business Rules Extraction (Erlang/Elixir)

Standalone reference for identifying business rules in BEAM-based codebases.
Static analysis only; no runtime introspection or vendor-specific tooling assumed.

---

## Candidate Patterns

| Pattern | Business-rule signal | Confidence guidance |
|---|---|---|
| Function clauses and guards | Partition input populations and outcomes | High when the full clause set is visible |
| Behaviour callbacks and protocol implementations | Type/module-specific enforcement | High when implementation and caller are traceable |
| Validation pipelines | Field and record constraints | High with explicit predicates |
| Persistent constraints and migrations | Structural or transitional data policy | Separate enduring constraints from one-time conversion |
| Configuration reads | External thresholds, modes, and eligibility flags | Cite both definition and enforcement when non-secret |
| Scheduled messages/jobs | Stakeholder-visible timing and expiry | Exclude generic polling and housekeeping |
| Process state transitions | Domain state/outcome changes | Exclude mailbox and lifecycle mechanics |
| Macros and parse transforms | Generated guards or decisions | Lower confidence unless invocation and definition establish behavior |
| Catch-all clauses | Default/fallback outcomes | Confirm ordering against preceding clauses |

## Module & Application Signals

- `.app.src` / `mix.exs` declare application boundaries and dependencies.
- Umbrella children (`apps/`) are independent OTP apps; inter-app calls reveal domain boundaries.
- Circular deps across apps signal entangled rules requiring split.
- Public API (`-export` / `def`) invoked from router/controller/handler = rule entry point.
- Helpers called from one site = implementation detail; from multiple = shared rule.

---

## Patterns, Guards & Decision Tables

- Treat each function clause for a given name/arity as one decision branch.
- Clause order encodes priority; read the full ordered set before stating the decision.
- Guard expressions encode preconditions.
- `defguard` names a reusable constraint — extract as a named rule.
- Record defaults, struct defaults, and enforced keys are invariant candidates; confirm runtime use.
- The catch-all clause is the fallback outcome.

---

## Behaviours, Protocols & Polymorphic Dispatch

- `-behaviour` / `@behaviour` declares a contract; each callback body = rule candidate (BEHAVIOUR_CALLBACK).
- Missing callback impl = incomplete rule.
- `defprotocol` / `defimpl` — each impl is a type-specific rule variant (PROTOCOL_IMPL).
- `use Module` injects macro code — always trace to `__using__/1` source.

---

## State, Messages & Transitions

- GenServer/gen_server state shape = rule context.
- `handle_call` (sync) / `handle_cast` (async) / `handle_info` (event) bodies contain STATE_TRANSITION evidence.
- `init/1` return establishes initial invariants.
- Tuple-tagged messages form implicit protocols; pattern match on shape = rule trigger.
- `{:stop, reason, state}` return = termination policy (TERMINATION_POLICY — only extract when it changes stakeholder-visible outcome).

---

## Supervision & Lifecycle (extract only when stakeholder-visible)

Extract a supervision/restart/mailbox detail as a rule **only** when it changes:
- **Eligibility** — who/what qualifies for a service or action
- **Timing** — when something becomes available or expires
- **State** — domain state visible outside the process boundary
- **Outcome** — result delivered to a user, client, or downstream system

Otherwise treat as operational plumbing. Examples that **are** rules:
- DynamicSupervisor spawn-time policy gating entity creation (eligibility).
- `shutdown` timeout determining whether a client gets a response (outcome).
- `code_change/3` altering domain state shape during hot upgrade (state).

---

## Data & Validation

- Treat changeset-style pipelines and custom validators as ordered constraint candidates (`code`).
- Persistent schema constraints and migrations can duplicate application enforcement; compare all four dimensions before merge/conflict decisions.
- Data migrations may encode transitional computations or state changes; distinguish one-time technical conversion from stakeholder policy.

## Configuration, Scheduling, and Macros

- Trace application, compile-time, and runtime settings to every use. Different active values are scoped variants only when activation contexts are provably mutually exclusive; otherwise retain separate conflict-linked rules.
- Periodic processes, timeout handling, and scheduler entries are rules only when timing changes a stakeholder-visible eligibility, state, or outcome.
- Macros and parse transforms require invocation plus repository-local definition evidence. If static expansion is uncertain, lower confidence and ask an open question.

## Definition-Use and Cross-Module Comparison

- Trace exported functions, callbacks, protocol/behaviour implementations, messages, state fields, and configuration keys through callers and handlers.
- Register each enforcement site independently. Identical subject, condition, threshold, and outcome merge with multiple evidence entries.
- Any difference in those dimensions produces separate rules with bidirectional `conflicting_rule_ids`; clause order may explain runtime selection but never erases the discrepancy.
- Unused exports are dead-code candidates or external contracts, not automatically active rules.

## Evidence Layer Mapping

| Artifact | `layer` value |
|---|---|
| Function clauses, guards, callbacks, process handlers, structs/records | `code` |
| Query fragments and data-access expressions | `sql` |
| Persistent schema constraints and migration constraints | `db_constraint` |
| Periodic task or scheduler registration | `batch` |
| Message-driven state transitions, sagas, process workflows | `workflow` |
| Interactive form/live-view validation when present | `ui` |
| Application/runtime configuration and policy constants | `config` |
| Declarative decision tables or repository-local rule definitions | `rules_engine` |

## Extraction Checklist

- [ ] Enumerate applications, modules, behaviours, protocols, and entry points.
- [ ] Extract clause sets and guards as decision candidates with exact evidence.
- [ ] Trace messages and process state only where business state/outcomes change.
- [ ] Separate supervision, restart, and mailbox plumbing from stakeholder policy.
- [ ] Capture application and persistent constraints and compare duplicates.
- [ ] Trace settings, schedules, and macro definitions without execution.
- [ ] Lower confidence for unresolved macro/runtime dispatch.
- [ ] Apply bidirectional merge/conflict handling across modules and applications.
- [ ] Assign every evidence entry one canonical `layer` value.
