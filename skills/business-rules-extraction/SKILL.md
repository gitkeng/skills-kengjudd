---
name: business-rules-extraction
description: >-
  Statically extracts, documents, and verifies business rules from any codebase.
  Performs read-only analysis without building or executing code. Produces domain-decomposed
  rule catalogs with line-level evidence, acceptance criteria, and coverage accounting.
  Triggers on: extract business rules, document business logic, reverse engineer requirements,
  analyze legacy system, what does this system do, mine rules from code.
license: MIT
metadata:
  version: "1.0.0"
  updated: "2026-08-29"
  upstream: "gitkeng/aws-kiro-atx-lab .kiro/skills/business-rules-extraction @595f830 (upstream version 1.1.0)"
---

# Business Rules Extraction — Agent Skill

Extract every business rule from a codebase through static analysis. Never build, run, or
modify the target code. Every documented rule cites source evidence. Absence is evidence —
state explicitly when something does not exist.

## Constraints

- **Static only:** never compile, execute, or invoke the analyzed code or its tests.
- **Read only:** never modify any source file in the analyzed repository.
- **Evidence based:** every rule or claim references real files with line ranges and snippets.
- **Language agnostic vocabulary:** use "service component", "persistent entity", "scheduled job" — never framework-specific jargon in outputs.
- **Forward-slash relative paths** in all generated artifacts regardless of OS.

## Two-Pass Workflow

### Pass 1 — Inventory and Decomposition

1. Confirm inputs: repository root, output root, monorepo subtree scope (if any). Defaults: repository root = current working directory; output root = `business-rules-output/` under the working directory.
2. Detect languages and stacks from extensions, manifests, imports, shebangs, schemas, job definitions, and configuration files. Load relevant playbooks per the references table.
3. Classify every regular file: `analyzed` or `excluded` with a reason class (binary, generated, vendored, test, out-of-scope). Generated requires a marker or generator evidence; state test-code policy explicitly.
4. Inventory entry points, persistent entities, dependency signals, business capabilities, and domain boundaries. Use stack-appropriate signals: copybook/JCL flow (mainframe); import/package graphs (JVM, .NET, scripting); FK/stored-procedure call graphs (data layer).
5. Assign every persistent entity to exactly one domain or mark it `shared` — no orphans. Record the complete entity list in `manifest.json` field `entity_inventory`. If the codebase has no natural domain boundaries (e.g., a small monolith), use a single domain covering all source.
6. Write `manifest.json`, `coverage.json`, `00-index.md`, `glossary.md` seed, and domain plan. Calculate extraction order from dependency signals.
7. **Pass 1 gate:** validate the manifest against the shipped schema and apply the criteria represented by check classes 2 (entity ownership) and 7 (coverage accounting) before proceeding to Pass 2. The full CLI validator (`scripts/validate_output.py`) runs once the mandatory output scaffold exists (i.e., after at least one domain is complete).

### Pass 2 — Per-Domain Deep Extraction

For each domain in extraction order:

8. Load only the current domain's file slice. Choose a mining strategy:
   - **Top-down:** trace from UI fields and entry points inward.
   - **Bottom-up:** trace from outputs, DB constraints, and persistent writes outward.
   - **Hybrid:** combine both; prefer slicing from business variables over keyword scanning.
9. Mine across all applicable layers: code, SQL, database constraints/triggers, batch/schedulers, workflow/BPM, UI validation, configuration, rules engines. For every threshold, constant, or flag referenced in a candidate rule, trace backward to its definition site (copybook, config, constants, schema, enum) and include the definition as additional evidence when it supplies business meaning or a concrete value not visible at the enforcement site.
10. For each candidate rule: phrase atomically (no OR on condition, no AND on action); assign type and category per the taxonomy; collect evidence with file, line_start, line_end, snippet, and layer; link to features/workflows and glossary terms; set confidence and initial review status. Register every distinct enforcement location as a separate candidate — do not pre-merge at this stage.
11. **Candidate fingerprint and comparison.** After all files in the current domain are mined, group candidates by business object/data element + observable outcome. For every group with more than one candidate, compare four dimensions: (a) subject scope — same entity/actor population? (b) condition/trigger — same guard? (c) threshold — same numeric, temporal, or categorical boundary? (d) outcome — same business effect? Decision: ALL four identical across layers → MERGE into one rule with multiple evidence entries. ANY dimension differs (different threshold, different population scope, different outcome) → KEEP as SEPARATE rules with bidirectional `conflicting_rule_ids`; flag in `open_questions` as supplemental documentation but NEVER as a substitute for the structural link. Merely associated rules addressing different business concepts that reference the same entity → `related_rule_ids` only (see pitfalls.md §5).
12. Flag dead code (unreachable logic) and suspicious patterns (magic values, comment-contradicts-code) — never silently treat them as active business rules. Beware framework-default configuration: only extract a configuration value as a business rule if a stakeholder would need to know about it (see pitfalls.md §11).
13. Write the domain's `rules.json` (canonical), then render `business-rules.md`, `overview.md`, `features.md`, `workflows.md`, `validations.md`, `integrations.md`, `open-questions.md`, and `diagrams.md` (sequence, component, workflow in Mermaid).
14. Persist progress: write a marker file `domains/<slug>/.complete` after each domain so extraction is resumable. On resume, skip domains whose `.complete` marker exists.

### Cross-Domain Finalization

15. After all domains complete, run the cross-domain verification pass. This phase MAY update previously completed domain `rules.json` files solely to add bidirectional conflict/related links discovered during later domains. No other modifications to completed domain outputs are permitted. For single-domain extractions, this pass still executes within the domain: compare every rule pair sharing a business object, data element, or glossary term; re-apply the four-dimension comparison from step 11 and escalate any `related_rule_ids` link to `conflicting_rule_ids` where dimensions differ.
16. **Conflict audit gate.** Before finalization, verify: (a) every open-question entry mentioning cross-location divergence, redundancy, or discrepancy maps to either a merge (same outcome, multiple evidence) or bidirectional `conflicting_rule_ids`; (b) no unresolved discrepancy lacks a structural link; (c) produce a conflict count in the domain's `open-questions.md` confirming how many conflicts were detected and linked. Any unresolved discrepancy without a structural link is a verification failure — do not proceed to domain output.
17. Generate cross-cutting documentation, database schema reconstruction, the SME review workbook CSV, and optional exports (DMN tables, Gherkin features, flat CSV catalog).

### Verification

18. Run the verification pass: accuracy (statement matches code behavior), redundancy (merge/conflict applied — every multi-location enforcement resolved per step 11; no `related_rule_ids` pair where dimensions differ), completeness (coverage ledger accounts for all files), relevance (plumbing excluded, legacy hacks flagged). Confirm backward traces: every rule referencing a configurable threshold cites evidence from both the enforcement site and the definition/configuration source.
19. Run `scripts/validate_output.py <output-dir> --repo <repo-root>`. Fix all failures and rerun until exit 0. Extraction is not complete while any check fails.

## Rule Identity and Rerun Policy

IDs follow `BR-<domain-slug>-<nnn>` and are stable within a single extraction run. On rerun: carry IDs forward by evidence location and statement similarity; allocate new IDs above the prior per-domain maximum; mark vanished rules `obsolete`.

## Confidence and Status Defaults

- Confidence below `high` → status automatically set to `needs_review`.
- Status transitions: `extracted` → `needs_review` → `validated` | `rejected` | `obsolete`.
- Reviewer and date fields are for SME use during the validation loop.

## Fact Routing

Facts (stable truths about business entities) are normally captured as evidence-linked glossary entries or database documentation. Promote a fact to a BR record only when it is business-significant: an SME would need to confirm it or could dispute it.

## Edge-Case Policies

- **Standard exclusions:** binary, generated (requires marker evidence), vendored, test code (policy stated in manifest), out-of-scope.
- **Monorepo:** record subtree scope in the manifest; paths are relative to the scoped root.
- **Oversized files:** subdivide by logical region (class, function block, section); retain one coverage record per physical file.
- **Encoding tolerance:** attempt UTF-8, fall back to Latin-1; for mainframe EBCDIC transfers, note encoding in coverage and process readable content. Report undecodable files as coverage findings — never crash.
- **Unlisted languages:** identify entry points, state, persistent data, boundaries, dependency declarations, conditional transformations, side effects, and business vocabulary. Trace business variables through definitions and uses. Document syntax-specific uncertainty. Worked example for Go: entry points = `main()` and HTTP handler registrations; state = struct fields and database models; boundaries = package imports; conditional transformations = `if`/`switch` on domain variables; side effects = database writes, external API calls; business vocabulary = exported function/type names matching domain terms.

## Output Tree

```
business-rules-output/
├── 00-index.md
├── manifest.json
├── coverage.json
├── coverage-report.md
├── glossary.md
├── open-questions.md
├── review-workbook.csv
├── domains/<slug>/
│   ├── rules.json          # canonical machine-readable catalog
│   ├── business-rules.md
│   ├── overview.md
│   ├── features.md
│   ├── workflows.md
│   ├── validations.md
│   ├── integrations.md
│   ├── open-questions.md
│   └── diagrams.md
├── cross-cutting/
├── database/
└── exports/                 # optional: CSV, Gherkin, DMN tables
```

## Stop Conditions

- Do not proceed past Pass 1 until the manifest passes schema validation and the entity-ownership (class 2) and coverage-accounting (class 7) criteria are satisfied.
- Do not declare a domain complete until its `rules.json` passes schema validation.
- Do not declare extraction complete until all ten validator checks pass with `--repo`.
- If domain boundaries cannot be determined (e.g., trivial or homogeneous codebase), collapse into a single domain covering all analyzed source and document the decision in `manifest.json`.
- If a file cannot be analyzed (encoding failure, extreme size, unknown binary), exclude with reason and continue — never halt the full extraction for one file.

## References

All paths below are relative to this skill's own directory, not the analyzed
repository. When the skill is installed as a symlink, resolve it first
(`readlink -f <this-skill-dir>`) and prefix every reference and script path with
the resolved directory — for example
`python3 <skill-dir>/scripts/validate_output.py <output-dir> --repo <repo-root>`.

Load each reference file only when its condition is met:

| File | Load when… |
|------|-----------|
| `references/rule-schema.md` | Writing or reviewing any `rules.json` |
| `references/taxonomy.md` | Assigning `rule_type` or `category` to any rule |
| `references/output-templates.md` | Creating any output file for the first time |
| `references/pitfalls.md` | Reviewing extraction results or encountering ambiguous code |
| `references/sme-validation.md` | Generating SME artifacts or preparing a validation session |
| `references/playbooks/mainframe.md` | Target contains COBOL, JCL, PL/I, RPG, or CICS artifacts |
| `references/playbooks/jvm.md` | Target contains Java or Kotlin source |
| `references/playbooks/dotnet.md` | Target contains C# or VB.NET source |
| `references/playbooks/scripting.md` | Target contains Python, Ruby, PHP, JavaScript, or TypeScript |
| `references/playbooks/go.md` | Target contains Go source, modules, or workspace artifacts |
| `references/playbooks/rust.md` | Target contains Rust source, crates, or workspace artifacts |
| `references/playbooks/dart-flutter.md` | Target contains Dart or Flutter source and project artifacts |
| `references/playbooks/typescript-react-next.md` | Target contains TypeScript, React, or Next.js source and project artifacts |
| `references/playbooks/native.md` | Target contains C or C++ source, headers, or build manifests |
| `references/playbooks/apple.md` | Target contains Swift or Objective-C source and project artifacts |
| `references/playbooks/beam.md` | Target contains Erlang, Elixir, OTP, or umbrella-project artifacts |
| `references/playbooks/automation.md` | Target contains Bash or PowerShell scripts, modules, or scheduler definitions |
| `references/playbooks/enterprise-legacy.md` | Target contains ABAP or PowerBuilder source/export artifacts |
| `references/playbooks/data-layer.md` | Target contains SQL, stored procedures, triggers, or schema definitions |
| `references/playbooks/scale.md` | Target exceeds 50K LOC or 500 source files |
| `scripts/validate_output.py` | Running mechanical validation of extraction output |
| `assets/manifest.schema.json` | Validator reads this at runtime; also reference when constructing manifest |
| `assets/rules.schema.json` | Validator reads this at runtime; also reference when constructing rules catalogs |

## Updating

This skill is versioned via `metadata.version` (see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`. Use the command
that matches how it was installed.

**Git clone + symlink install** — run from the repository root:

```bash
./scripts/update.sh business-rules-extraction
```

If this skill directory is a symlink (the normal install), resolve it with
`readlink -f <this-skill-dir>`; the repo root is two directories above the
resolved path.

The script fetches `origin/main`, compares this skill's `metadata.version`,
shows this skill's pending commits, and pulls after confirmation.

**Claude Code plugin install** — the plugin cache has no `.git`, so
`update.sh` cannot run there:

```bash
claude plugin update skills-kengjudd@kengjudd
```

After updating, restart the agent session so the new version loads.
