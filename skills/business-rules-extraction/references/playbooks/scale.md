# Scale Playbook

Strategy for extracting business rules from large codebases (50K+ LOC, 500+ source files). Implements the two-pass resumable architecture.

## Two-Pass Structure

### Pass 1 — Whole-Repository Inventory (read everything once, write decomposition)

1. **Full file scan:** Walk the entire file tree. Classify each file by extension, markers, and content sampling. Build the coverage ledger (analyzed/excluded with reasons).
2. **Stack detection:** Identify all languages and frameworks from extensions, manifests, build files, shebangs, and configuration. Record primary and secondary languages.
3. **Entity inventory:** Identify persistent entities from schema definitions, model/entity classes, table references, COBOL FD/copybook records, and data-layer DDL across the full codebase.
4. **Dependency graph construction:**
   - Mainframe: copybook inclusion graph + JCL job step sequencing + CALL/LINK references.
   - JVM: import/package graph + module dependencies + bean wiring.
   - .NET: namespace/project reference graph + interface implementations.
   - Scripting: import/require graph + route registrations + configuration references.
   - Data layer: FK graph + stored procedure call graph + trigger-to-table mapping.
5. **Domain boundary detection:** Cluster entities and their associated code using dependency signals, directory structure, namespace/package groupings, and shared-entity analysis. Assign each entity to exactly one domain or mark as shared with justification.
6. **Write Pass 1 outputs:** `manifest.json`, `coverage.json`, `00-index.md`, initial `glossary.md`, domain directory structure. These are committed before starting Pass 2.
7. **Calculate extraction order:** Sort domains by dependency depth (leaf domains first, domains depended upon by many others last) so that cross-domain references are available when processing dependent domains.

### Pass 2 — Per-Domain Deep Extraction (one domain at a time)

For each domain in extraction order:

1. **Load only the current domain's file slice** — the files assigned to this domain in the manifest, plus any shared-entity definitions referenced by this domain.
2. **Load relevant stack playbooks** — only those matching the technologies present in this domain's slice.
3. **Execute the deep extraction** following the methodology in SKILL.md steps 7–12.
4. **Persist immediately:** Write the domain's complete output (`rules.json`, all `.md` files) before moving to the next domain.
5. **Update progress:** Append to a progress marker so that if extraction is interrupted, the next session can identify which domains are complete and resume from the next incomplete domain.

### Resumability Contract

- After Pass 1, any interruption can resume at Pass 2 for the first incomplete domain.
- After any domain in Pass 2, the completed domains' outputs are final and are not re-extracted.
- The verification pass (SKILL.md step 18) and cross-domain outputs (step 15–17) run only after all domains are complete.
- If the executing agent's context window reaches capacity during a domain, it should persist partial findings, document the interruption, and signal that the domain needs re-extraction from the beginning of that domain (not the whole repository).

## Chunk Size Management

A chunk is one domain's file slice. For most codebases, this is manageable. When a single domain's slice is still too large:

- **Subdivide by sub-capability:** Split the domain into feature-aligned sub-slices, extract each independently, then merge `rules.json` files (ensuring ID uniqueness).
- **Oversized individual files:** Files exceeding 2000 lines are processed by logical section (class, function group, paragraph/section in COBOL). One coverage record per physical file; extraction notes track which sections are processed.
- **Target chunk budget:** Aim for 200–500 files or 30K–50K LOC per extraction pass. Adjust based on code density and complexity.

## Worked Walkthrough — 100K+ LOC System

**Scenario:** A financial services application with 120K LOC across Java services (60K), PL/SQL stored procedures (35K), JavaScript frontend (20K), and configuration/SQL migrations (5K). Approximately 800 source files after exclusions.

### Pass 1 Execution

1. **File scan (minutes):** Walk 1200 total files. Exclude 400 (node_modules vendored, compiled JS bundles with source maps, test suites, binary assets, generated API stubs marked with `@Generated`). Remaining: 800 analyzed files.

2. **Stack detection:** Primary languages: Java 17 (Spring Boot), PL/SQL. Secondary: TypeScript (React), SQL (Flyway migrations). Playbooks to load: jvm.md, data-layer.md, scripting.md.

3. **Entity inventory:** Scan JPA `@Entity` classes (45 entities), PL/SQL table references in procedures (12 additional tables without Java entities), migration DDL (confirms schema). Total: 57 persistent entities.

4. **Dependency graph:**
   - Java: 12 Maven modules; import graph shows 5 tightly coupled clusters and 2 utility modules.
   - PL/SQL: Procedure call graph shows 3 procedure groups by calling patterns.
   - FK graph: 57 tables with 89 foreign keys forming 6 connected components.
   - JavaScript: Route structure shows 4 top-level feature areas.

5. **Domain detection:** Cross-referencing clusters:
   - `accounts` (8 entities, 2 Java modules, 1 PL/SQL group)
   - `lending` (12 entities, 2 Java modules, 1 PL/SQL group)
   - `payments` (9 entities, 1 Java module, PL/SQL procedures)
   - `compliance` (6 entities, 1 Java module, scheduled jobs)
   - `reporting` (5 entities, PL/SQL packages, no Java service)
   - `customer-portal` (3 entities, JavaScript frontend + API gateway)
   - Shared: `audit_log`, `reference_data`, `system_config` (3 entities across multiple domains)

6. **Write outputs:** manifest.json with 6 domains + 3 shared entities, coverage.json with 800 records, directory scaffolding.

7. **Extraction order:** `reporting` → `accounts` → `customer-portal` → `payments` → `lending` → `compliance` (dependency depth ordering: compliance depends on all others for audit integration).

### Pass 2 Execution (per domain)

**Domain: accounts (example)**
- Load: 85 files (15K LOC Java + 8K LOC PL/SQL + 3K LOC migrations)
- Mining: hybrid strategy — top-down from REST controllers (12 endpoints) + bottom-up from 23 CHECK constraints and 8 triggers
- Findings: 38 candidate rules → after plumbing removal and merge: 29 rules across 4 types, 5 categories
- Write: `domains/accounts/rules.json` + all documentation files
- Duration estimate: one focused extraction session per domain

**Cross-domain phase (after all domains):**
- Verify cross-domain rule links and shared-entity consistency
- Generate: `cross-cutting/` documentation, final `glossary.md`, `review-workbook.csv`
- Run validator: `validate_output.py business-rules-output/ --repo /path/to/source`

### Scale Observations

- Total extraction: 6 domain passes + 1 inventory pass + 1 cross-domain pass = 8 sessions
- Total rules expected: 150–250 for a system of this size and complexity
- Key risk: PL/SQL procedures with >1000 lines require intra-file chunking by procedure
- Encoding: PL/SQL source transferred from database; confirm UTF-8 export
- Test code (25K LOC excluded) means actual business-logic density is concentrated in the 95K analyzed LOC

## Performance Characteristics

Extraction cost scales with code size and complexity, not with rule count (Earls, Embury & Turner, BT Technology Journal 20(4), 2002). Implications:

- A 10K LOC system with 200 complex rules takes less extraction effort than a 200K LOC system with 50 simple rules spread across many files.
- Prioritize domains by business value and change frequency, not by estimated rule count.
- The two-pass architecture ensures that the expensive full-scan happens once; subsequent domain passes operate on reduced file sets.
