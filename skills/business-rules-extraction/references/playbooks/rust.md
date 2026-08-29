# Rust Business-Rules Extraction Playbook

## Detection

Confirm presence of at least two: `Cargo.toml` at root or workspace, `*.rs` source files with `mod`/`use` declarations, `Cargo.lock`, or targets referencing `cargo build`/`cargo test`. If confirmed, apply this playbook.

## Artifact → Evidence Enum

| Artifact / Pattern | Evidence Layer |
|--------------------|---------------|
| Domain structs with validation in `new()` / builder methods | `code` |
| `impl` blocks with guard clauses, `if`/`match` business predicates | `code` |
| Enum variants representing domain states; `match` arms encoding transitions | `code` |
| `guard` expressions in match arms (conditional constraints) | `code` |
| Custom error enums (`DomainError`, `ValidationError`) — each variant = violation | `code` |
| Macro invocations expanding to validation predicates (`validate!`, `ensure!`) | `code` |
| Proc-macro-generated constraints (`#[derive(Validate)]`, `#[rule(...)]`) | `code` |
| `require!` / `assert!` with business predicates (not debug-only) | `code` |
| SQL queries via `sqlx`, `diesel`, `sea-orm` with WHERE / HAVING clauses | `sql` |
| Migration files (`.sql`, `up.sql`/`down.sql`) defining schema rules | `sql` |
| CHECK constraints, UNIQUE indexes, NOT NULL in migrations or annotations | `db_constraint` |
| Foreign key relationships in schema definitions | `db_constraint` |
| `#[sea_orm(unique)]`, `#[diesel(check = "...")]` or equivalent | `db_constraint` |
| Scheduled tasks (`tokio-cron-scheduler`, `apalis`, spawned periodic loops) | `batch` |
| Retry/expiry/reconciliation background jobs | `batch` |
| Event handlers, message consumers (`async fn handle(event: E)`) | `workflow` |
| State machine transitions across async boundaries | `workflow` |
| Saga / orchestration patterns coordinating multiple steps | `workflow` |
| Channel-mediated sequencing with business-meaningful ordering | `workflow` |
| Request validation in handler/route functions | `code` |
| Custom request-extractor implementations that reject invalid input | `code` |
| Response shaping with business-driven status selection | `code` |
| `config` crate values, env vars, TOML/YAML-loaded thresholds and toggles | `config` |
| `lazy_static!` / `once_cell` constants sourced from external config | `config` |
| Feature flags read at runtime (not `#[cfg]` compile-time gates) | `config` |
| Drools-like rule definitions, decision-table YAML/JSON, policy DSL files | `rules_engine` |
| Embedded scripting (Rhai, Lua via `mlua`) evaluating business predicates | `rules_engine` |

## Compile-Time vs Runtime Enforcement

| Construct | Classification |
|-----------|---------------|
| Trait bounds (`T: Send + Sync`, `T: Validator`) | Compile-time type constraint — NOT runtime enforcement |
| Generic constraints, associated types | Compile-time — skip unless paired with runtime check |
| `#[cfg(feature = "...")]` — code inclusion/exclusion at build | Compile-time gate — NOT runtime enforcement |
| Newtype wrappers with no validation in constructor | Compile-time — type safety only |
| Enum exhaustiveness (non-`_` match) | Compile-time completeness — not a business rule |
| Runtime `if`/`match` on feature-flag value from config | Runtime enforcement — extract as `config` evidence |
| Validation logic inside `TryFrom`, `FromStr`, builder `.build()` | Runtime enforcement — extract as `code` evidence |
| `Drop` impl with business side-effects (not just dealloc) | Runtime enforcement — extract as `code` evidence |

Compile-time traits and types establish contracts but do not enforce rules at runtime. Only extract when paired with runtime validation logic.

## Feature Gates & Config Variants — Conflict Rules

When the same business concept appears under different `#[cfg(feature)]` blocks or config-driven branches:

1. If variants differ in **scope** (which entities affected), **condition** (predicates checked), **threshold** (numeric limits), or **outcome** (accept vs reject vs transform) → record as **separate rules** with a **bidirectional CONFLICT** flag.
2. Each side of the conflict cites its activation condition and evidence location.
3. Do NOT merge variants that differ on any of the four dimensions above into a single rule.

| Scenario | Action |
|----------|--------|
| `#[cfg(feature = "premium")]` applies 20% discount; default applies 5% | Two rules, CONFLICT — threshold differs |
| `#[cfg(feature = "strict")]` rejects negative totals; default allows zero | Two rules, CONFLICT — condition and outcome differ |
| Config `max_retries=3` in prod vs `max_retries=10` in staging | Two rules, CONFLICT — threshold differs per environment |
| Same validation, feature merely toggles code path inclusion | One rule — no semantic difference at runtime |
| Trait bound differs but no runtime behavior change | Not a rule — compile-time only |

## Crate & Module Signals

- `Cargo.toml` workspace `members` lists crates; domain logic in `domain/`, `core/`, `lib/` crates.
- `pub use` re-exports define public API surface — these are contract boundaries.
- `internal/` or `pub(crate)` items are private invariants; still extract if they enforce constraints at runtime.
- Follow `use crate::domain::` imports to locate rule consumers.

## Enum States & Match Transitions

- Each enum variant naming a business state is a rule candidate.
- Match arms = transition rules; guards (`if expr`) = conditional constraints.
- Missing arms in exhaustive match = compiler-enforced exclusion (compile-time, not runtime rule).
- Multiple `impl` blocks or trait impls for the same type with differing behavior per variant = variant rules.

## Macros

- **Invocation**: extract predicate + message as a business rule (`validate!(total > 0, "positive")`).
- **Definition**: `macro_rules!` and proc-macro crate source may generate constraints — inspect expansion.
- Generated code from `#[derive(...)]` with custom proc macros: trace to proc-macro source for rule logic.

## Persistence & Data Integrity

- Repository trait methods (`fn find_active_orders`) encode scoped views — extract WHERE-equivalent conditions.
- `sqlx::query!` / `diesel` DSL queries embed filtering rules — map to `sql` evidence.
- Schema migrations with CHECK, UNIQUE, FK → `db_constraint` evidence.

## Background Jobs & Temporal Rules

- Scheduled tasks encode temporal rules: retry cadence, expiry windows, reconciliation intervals.
- Each job's trigger condition and periodicity is a rule (extract schedule + business purpose).
- Timeout values with business justification (SLA, freshness guarantee) → extract as `batch` or `workflow`.

## Ownership & Concurrency — Policy Filter

| Signal | Extract? |
|--------|----------|
| `Arc<Mutex<T>>` protecting domain aggregate with business invariant | Yes — serialized access is a consistency rule |
| Typed channel enforcing business ordering or priority | Yes — sequencing rule → `workflow` |
| Context/timeout with business-defined deadline (SLA) | Yes — temporal constraint |
| Generic `Mutex`, `RwLock` for thread safety only | No — plumbing |
| `Send + Sync` bounds | No — compile-time only |
| Lifetime annotations | No — memory safety plumbing |

## Merge & Conflict Resolution

| Overlap | Resolution |
|---------|-----------|
| Same semantics, different locations | Merge into one rule citing all evidence sites |
| Same concept, different threshold/condition/scope/outcome | Separate rules with bidirectional CONFLICT |
| Macro-generated vs hand-written (same semantics) | Prefer hand-written; cite both |
| Config value vs hard-coded constant (same semantics) | Config = runtime-overridable; constant = fixed; note override relationship |
| Compile-time gate vs runtime flag (same concept) | Runtime flag is the rule; compile-time gate is build configuration |
| Contradictory rules across crates | CONFLICT — cite both, do not resolve |

## Checklist

- [ ] Workspace/crate inventory completed
- [ ] Enum states and match transitions catalogued with evidence layer
- [ ] Domain error variants listed as `code` evidence
- [ ] Feature-gate and config variants checked for scope/condition/threshold/outcome differences
- [ ] Bidirectional conflicts flagged for differing variants
- [ ] Compile-time-only constructs excluded from runtime rules
- [ ] Macros (invocation + definition) reviewed; generated constraints traced
- [ ] Persistence queries mapped to `sql` / `db_constraint`
- [ ] Background jobs mapped to `batch`; event handlers to `workflow`
- [ ] Config thresholds and toggles captured as `config` evidence
- [ ] Ownership/concurrency constructs filtered (policy vs plumbing)
- [ ] Merge/conflict table populated
