# Go Business-Rules Extraction Playbook

## 1 · Detection

Confirm presence of at least two: `go.mod` at root, `*.go` files with `package` declarations, `go.sum`, or build targets referencing `go build`/`go test`. If confirmed, apply this playbook.

## 2 · Inventory Pass

| Artifact | Location |
|----------|----------|
| Module path & version | `go.mod` first line |
| Direct dependencies | `require` block in `go.mod` |
| Build entry points | `package main` + `func main()` |
| Internal packages | `internal/` directories |
| Generated code | `// Code generated` header — skip for rule extraction |
| Test files | `*_test.go` — may encode rule assertions |

## 3 · Dependency Signals

### Module / Package / Import
- **Module boundary** (`go.mod`) defines versioning and dependency scope.
- **Package = compilation unit** — each directory is one package; name declares intent.
- **`internal/`** enforces visibility; rules inside cannot be consumed outside the parent.
- Standard-library vs third-party imports reveal domain concerns (`crypto/`, `database/sql`, `net/http`).
- Blank imports (`_ "pkg"`) signal side-effect registration (drivers, codecs).

### Interfaces
- Small interfaces (1–3 methods) in consuming packages define **contracts** — these are rules.
- Interfaces in `domain/` or `core/` represent policy boundaries.
- Satisfaction is implicit; find implementors via method-signature matching.

### Handlers & Routes
- HTTP handlers and framework router registrations map to use-case entry points.
- Middleware chains encode cross-cutting rules (auth, rate-limit, logging).
- gRPC service interfaces (`pb.UnimplementedXxxServer`) define API contracts.

### Jobs & Workers
- Background goroutines launched in `main`/`init` encode scheduling rules.
- Tickers and `time.AfterFunc` indicate temporal business rules.
- Bounded worker pools encode throughput constraints.

### Message Consumers & Producers
- Queue/topic subscriptions are event-driven rule triggers.
- Message struct types define event schemas — fields and tags encode invariants.
- Publish calls reveal downstream rule propagation.

### Database Interactions
- ORM model structs, migration files, raw SQL encode persistence rules.
- Query builders in repository packages encode data invariants.
- Transaction boundaries (`tx.Begin`…`tx.Commit`) reveal atomicity requirements.

## 4 · Struct Tags & Validation

| Tag prefix | Rule type |
|-----------|-----------|
| `validate:"required,min=1"` | Field-level invariants |
| `json:"field,omitempty"` | Serialization optionality |
| `db:"column_name"` | Persistence mapping |
| `binding:"required"` | Request-binding constraints |
| Custom tags | Domain-specific annotations |

Extract every tagged struct as a candidate rule carrier. Cross-reference with `validator.Struct()` calls or validation middleware.

## 5 · Definition-Use Analysis

For each candidate rule:
1. **Definition site** — struct, const block, interface, or config key.
2. **Enforcement site(s)** — if-guards, validators, middleware.
3. **Violation handling** — error return, panic, or log-and-continue.

Trace definition → enforcement. A rule with no enforcement is aspirational; flag it.

## 6 · Goroutines & Channels — Policy vs Plumbing

| Signal | Classification |
|--------|---------------|
| Channel enforcing ordering or priority | **Policy** — extract |
| Channel for fan-out/fan-in mechanics | Plumbing — skip |
| `select` with business-meaningful timeout | **Policy** — timeout is a rule |
| `sync.Mutex` protecting shared state | Plumbing — skip |
| Context cancellation with business-defined deadline | **Policy** |
| `errgroup` limiting concurrency to N | **Policy** if N is a business constraint |

Extract the *why* (SLA, fairness, ordering), not the *how* (buffer size, direction).

## 7 · Build Tags & Config Variants

- `//go:build` constraints partition behavior by environment, OS, or feature flag.
- Tagged files may contain environment-specific enforcement — each distinct threshold/condition is a separate candidate rule.
- Config structs loaded from env/files encode tunable business parameters.
- `const` blocks and `iota` enumerations define fixed business vocabularies.

Record each with its activation condition as a conditional rule.

## 8 · Rule vs Plumbing

| Keep as Rule | Discard as Plumbing |
|-------------|-------------------|
| Domain constraint a stakeholder would recognize | Exists only for technical orchestration |
| Requires business approval to change | Developer refactors freely |
| Asserted in tests as behavioral expectation | Tested only for coverage |
| Named concept (policy, limit, threshold) | Generic utility (retry, marshal, log) |
| Survives language change | Tied to Go-specific mechanics |

When uncertain, keep and mark confidence LOW.

## 9 · Merge & Conflict Resolution

Compare candidates grouped by business object + observable outcome across four dimensions: (a) subject scope, (b) condition/trigger, (c) threshold, (d) outcome.

**Merge** into one rule with multiple evidence entries ONLY when ALL four dimensions are identical across locations/layers. Technical-only differences (error message format, exception type vs error value) are not dimensional differences.

**Separate rules with bidirectional `conflicting_rule_ids`** when ANY dimension differs:
- Different thresholds (UI validates max 100, DB column is 80).
- Different population scope (one path exempts admins, another applies universally).
- Different conditions (one checks `>=`, another checks `>`).
- Different outcomes (one rejects, another truncates silently).

Never classify a dimensional difference as merely a "variant" or resolve it by declaring one location wins. Both rules stand; both get `conflicting_rule_ids` pointing at each other; both get `needs_review` status with an open question explaining the observed divergence.

**`related_rule_ids`** applies only when rules address genuinely different business concepts that share an entity or term (e.g., "order must be active to add items" vs "order must be active to issue refund").

## 10 · Artifact → Evidence Layer Mapping

When recording evidence, assign `layer` based on the source artifact:

| Go Artifact | Evidence `layer` |
|-------------|-----------------|
| `.go` source — if-guards, switch cases, method logic | `code` |
| Raw SQL strings, query-builder calls, `.sql` files | `sql` |
| Migration `ALTER TABLE … CHECK`, unique indexes, FK declarations | `db_constraint` |
| Cron jobs, ticker loops, scheduled goroutines, job-queue consumers | `batch` |
| State-machine transitions, saga orchestrators, multi-step pipelines | `workflow` |
| Template files, form validation, HTTP request-binding constraints | `ui` |
| Env vars, config structs, YAML/TOML/JSON config, `const`/`iota` blocks, build tags | `config` |
| Embedded rule DSLs, policy engines (OPA/Rego, CEL expressions) | `rules_engine` |

Every evidence entry must use exactly one of these eight values. When a single source file contains mixed concerns (e.g., a handler with inline SQL), assign per-snippet based on what the snippet itself represents.

## 11 · Checklist

- [ ] All `package main` entry points scanned
- [ ] Interfaces in domain packages cataloged as contracts
- [ ] Struct tags parsed for validation and persistence rules
- [ ] Handler/middleware chains traced for cross-cutting rules
- [ ] Background jobs and temporal triggers identified
- [ ] Message schemas and event flows mapped
- [ ] Database migrations and query constraints captured
- [ ] Goroutine/channel patterns classified (policy vs plumbing)
- [ ] Build-tag variants recorded with activation conditions
- [ ] Constants and enumerations checked for business vocabularies
- [ ] Conflicts flagged with bidirectional `conflicting_rule_ids`
- [ ] Each evidence entry assigned a canonical layer value
- [ ] Generated code excluded; test files reviewed for hidden rules
