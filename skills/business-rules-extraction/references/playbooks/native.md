# Native (C/C++) Business-Rules Extraction Playbook

> Standalone, static, read-only, vendor-neutral. No compilation required.

---

## 1 Detection & Inventory

| Signal | Files / Patterns |
|--------|-----------------|
| C source | `*.c`, `*.h` |
| C++ source | `*.cpp`, `*.cxx`, `*.cc`, `*.hpp`, `*.hxx`, `*.hh`, `*.tpp` |
| Build manifests | `Makefile`, `CMakeLists.txt`, `meson.build`, `*.vcxproj`, `BUILD`, `SConstruct` |
| Package configs | `conanfile.txt`, `vcpkg.json`, `*.pc.in` |
| Generated | `*_generated.h`, `*.pb.h`, `*_auto.c` — tag as generated, skip for rules |

Inventory action: recursively list all source/header files; note directory layout. Record build-manifest locations.

---

## 2 Header / Source / Build-Manifest Parsing (No Compile)

### 2.1 Include Graph
- Parse `#include "..."` (project-local) vs `#include <...>` (system/vendor).
- Build directed include-graph; identify module clusters by strongly-connected components.

### 2.2 Build Flags & Definitions
- Extract `-D` defines, `-I` paths, `target_compile_definitions` from CMake/Make/Meson.
- Per-target flag sets reveal **feature toggles** and **platform variants**.

### 2.3 Source Segmentation
- Separate into: public API headers, internal headers, implementation, tests, platform-specific dirs.

---

## 3 Include / Call / Data-Flow Analysis

### 3.1 Call Graph (Static Approximation)
- Match call-sites to definitions by name + arity; for C++ overloads record all candidates.
- Trace public API entry points → internal helpers → leaf computations.

### 3.2 Data Flow
- Track struct/class instances from allocation through field assignment to consumption.
- Follow pointer/reference parameters one level interprocedurally; mark globals as shared-state anchors.

### 3.3 Include-Driven Dependency
- Map which business-logic headers are included by which implementation files.
- Flag circular includes as potential rule-boundary confusion.

---

## 4 Preprocessor Variants & Build Flags

| Construct | Rule Relevance |
|-----------|---------------|
| `#ifdef FEATURE_X` / `#if defined(...)` | Conditional business logic — extract both branches as variant rules |
| `#if PLATFORM == ...` | Platform-specific behavior — see §11 for conflict handling |
| `#ifndef NDEBUG` / `#ifdef _DEBUG` | Debug-only paths — exclude from production rules |
| `#define CONSTANT value` | Domain constants — capture as rule parameters |
| `#define MACRO(args) ...` | May encode business logic — see §6 |

Action: for each `#if`/`#ifdef` block containing domain logic, emit one rule variant per branch with the controlling condition as a precondition.

---

## 5 Structs / Enums / Tagged Unions

- **Structs/classes**: field names, types, and comments encode domain entities. Map to domain model.
- **Enums**: enumerate domain states/categories. Distinguish domain enums (e.g., `OrderStatus`) from system enums (e.g., `errno`).
- **Tagged unions** (`union` + discriminator, `std::variant`): each variant = domain case — extract per-tag rules.
- **Bitfields / flags**: document flag semantics; each combination may encode a rule.

---

## 6 Function Pointers / Templates / Macros

### 6.1 Function Pointers & Callbacks
- Identify `typedef`/`using` for function-pointer types.
- Trace assignment sites to determine concrete backing functions.
- Strategy tables (arrays of fn-pointers indexed by enum) encode dispatch rules.

### 6.2 Templates (C++)
- Each explicit/partial specialization may encode a distinct rule variant.
- SFINAE / `if constexpr` branches → conditional rules keyed on type traits.

### 6.3 Macros
- Expand macro bodies textually; if expansion contains control flow or domain calculations, treat as rule candidate.
- Flag **macro uncertainty** when expansion depends on call-site context — mark confidence `low`.

---

## 7 Persistence / Embedded SQL / Configuration

| Pattern | Extraction |
|---------|-----------|
| Embedded SQL (`"SELECT..."`, EXEC SQL) | Parse SQL; map queries/mutations to domain operations |
| File I/O with structured formats | Identify record layout from struct serialization |
| Config reads (`fopen` + key parsing, `getenv`) | Map config keys to parameterized rules |
| DB client calls (ODBC, SQLite, libpq) | Trace bound parameters back to business data |
| Memory-mapped / shared memory | Identify persisted domain state |

---

## 8 Definition-Use Chains

- For each domain variable/field, trace from definition to all uses (reads, comparisons, arguments).
- Highlight **guard conditions**: `if (field op value)` where field is domain data → candidate rules.
- Identify dead definitions (never used in domain logic) — exclude from rules.
- Track cross-function def-use through parameters and return values.

---

## 9 Business-Rule vs Plumbing Classification

| Category | Heuristic — EXCLUDE from business rules |
|----------|----------------------------------------|
| Memory management | `malloc`/`free`/`new`/`delete`, RAII, smart-pointer ops |
| Concurrency | `mutex`, `lock_guard`, `atomic`, `pthread_*`, semaphore ops |
| Build/link | `#pragma`, linker directives, visibility attributes |
| Error plumbing | `errno` checks, `try`/`catch` system exceptions, null guards |
| Logging/tracing | `printf`-debug, `syslog`, `LOG_*` macros |
| Platform glue | OS-adaptation wrappers that **only** translate API signatures without altering domain behavior |

**INCLUDE**: domain validation, state transitions, calculations, policy enforcement, authorization, thresholds, workflow sequencing — regardless of file location. Infrastructure files (build configs, platform layers, utilities) may embed business policy (rate limits, size constraints, timeout policies, feature gates). Evaluate whether each threshold or conditional changes stakeholder-visible eligibility, calculation, state, timing, access, or outcome before excluding it.

---

## 10 Macro Uncertainty

When a macro's expansion is ambiguous or context-dependent:
1. Document macro name, defined location, and all invocation sites.
2. Expand manually for each distinct call-site context.
3. If expansions diverge in domain behavior, emit one rule per variant.
4. Set `confidence.level` per expansion clarity: `high` (single expansion, clear), `medium` (multiple, consistent), `low` (context-dependent divergence or token-pasting obscures semantics).
5. Mark `low`-confidence macros `review.status = "needs_review"` with an entry in `open_questions`.

---

## 11 Cross-Platform & Preprocessor Conflict Handling

Platform-conditioned blocks (`_WIN32`, `__APPLE__`, `__linux__`, etc.) and preprocessor-selected thresholds require per-case judgment using subject scope, condition, threshold, and outcome:

**MERGE** into one rule with multiple evidence entries when subject scope, condition, threshold, and outcome are identical across platforms (only the API spelling differs).

**SEPARATE rules with bidirectional `conflicting_rule_ids`** when any dimension differs:
- Different numeric thresholds per platform (e.g., `MAX_PATH` 260 on Windows vs 4096 on Linux controlling a business validation).
- One platform enforces a constraint the other skips.
- Different outcomes for the same input on different platforms.

Each platform variant becomes its own rule. Both rules receive bidirectional `conflicting_rule_ids`, `review.status = "needs_review"`, and an `open_questions` entry explaining the divergence and possible design rationale.

---

## 12 Artifact → Evidence Layer Mapping

Every evidence entry requires a `layer` value from the canonical enum. Use this table to map C/C++ artifact types:

| Artifact type | Evidence `layer` value | Examples |
|---------------|----------------------|----------|
| `.c` / `.cpp` implementation files | `code` | Business logic functions, state machines, calculations |
| `.h` / `.hpp` public API headers | `code` | Domain type definitions, constraint constants, API contracts |
| Internal/private headers | `code` | Module-internal policy constants, struct invariants |
| Embedded SQL strings, EXEC SQL | `sql` | Queries and mutations inside C/C++ source |
| DB schema files (`.sql`) in repo | `db_constraint` | CHECK constraints, triggers, FK rules |
| CMake / Makefile / Meson definitions | `config` | Business-relevant `-D` thresholds, feature gates, size limits |
| `.ini` / `.cfg` / `.json` / `.yaml` config | `config` | Runtime policy values read via config APIs |
| Build-system conditional logic | `config` | Platform-specific policy selection in build manifests |
| UI resource files, form definitions | `ui` | Input masks, field length limits, validation patterns |
| Scheduler / cron definitions | `batch` | Timed job triggers with business cadence |
| State-machine / workflow descriptors | `workflow` | Transition definitions in declarative files |
| Rules-engine tables (decision tables, `.drl`) | `rules_engine` | Externalized business decision logic |

No artifact type is categorically excluded from rule mining. Evaluate each occurrence for a stakeholder-visible eligibility, calculation, state, timing, access, or outcome.

---

## 13 Extraction Checklist

- [ ] Inventory all source, header, and build files
- [ ] Build include-graph and identify module clusters
- [ ] Extract build-flag defines and feature toggles
- [ ] Parse structs/enums/unions into domain model
- [ ] Trace call graph from public API inward
- [ ] Identify function-pointer dispatch tables
- [ ] Expand and classify macros (flag low-confidence per §10)
- [ ] Extract embedded SQL / config-driven parameters
- [ ] Build definition-use chains for domain variables
- [ ] Classify each code region as business-rule or plumbing (§9 — evaluate infrastructure locations individually)
- [ ] Handle preprocessor variants: one rule per branch; merge or conflict-link per §11
- [ ] Map each evidence entry to a canonical layer value per §12
- [ ] Set `confidence`, `applicability`, and `open_questions` per rule schema; flag `needs_review` items
