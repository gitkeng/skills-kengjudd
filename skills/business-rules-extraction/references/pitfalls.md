# Pitfalls Reference

Common failure modes in business rule extraction and how to handle each.

## 1. Business Logic vs Technical Plumbing

The core difficulty of legacy rule extraction is separating business-meaningful rules from infrastructure code.

**Plumbing (exclude from rules catalog):**
- Connection pooling, retry/backoff logic, circuit breakers
- Logging, metrics, and telemetry instrumentation
- Serialization/deserialization boilerplate
- Framework lifecycle hooks (initialization, shutdown, health checks)
- Generic CRUD operations without business conditions
- HTTP routing, middleware registration, dependency injection wiring
- Memory management, caching infrastructure, thread synchronization

**Business logic (include):**
- Conditional behavior that an SME would recognize as a policy or constraint
- Calculations that produce business-meaningful values (prices, scores, dates)
- State transitions governed by domain conditions
- Access decisions based on business roles or data ownership
- Data transformations that enforce business format/structure requirements

**Decision test:** Would a business stakeholder need to know about this behavior to understand what the system does for its users? If yes → candidate rule. If only a developer maintaining infrastructure would care → plumbing.

## 2. Dead Code Masquerading as Active Rules

Code that is syntactically present but never reachable is not an active business rule.

**Detection signals:**
- Methods/functions with no callers in the codebase (confirm no external entry point)
- Conditional branches guarded by constants that always evaluate one way
- Code after unconditional returns, breaks, or throws
- Commented-out blocks (never treat comments as active logic)
- Feature flags permanently set to off with no toggle mechanism
- Deprecated annotations/markers with no remaining invocations

**Handling:** Document the rule with `applicability.state = "dead"` and a justification. Flag for SME review — dead code sometimes represents deactivated business capability that stakeholders intend to re-enable.

## 3. Magic Values and Hardcoded Thresholds

Literal values embedded in code without explanation are high-risk for misinterpretation.

**Examples:** `if (age >= 21)`, `MAX_RETRIES = 3`, `discount = 0.15`, `status == "X"`.

**Handling:**
- Search for the value in configuration, constants files, database seed data, and documentation to determine if it has an authoritative source.
- When the meaning is unambiguous from context (e.g., HTTP status 404), treat as plumbing.
- When the value controls business behavior but its origin is unclear, document the rule with confidence `medium` and add an open question: "What is the business basis for this threshold?"
- Never invent a business justification for a magic value.

## 4. Comment-Contradicts-Code

When a code comment describes behavior that differs from what the code actually does:

**Rule:** Always extract the rule from the CODE, not the comment. Document the contradiction in `open_questions` with both the comment text and the actual code behavior. Set confidence to `medium` and flag for SME review — the comment may reflect intended behavior that was never implemented, or outdated behavior that was changed without updating the comment.

**Never:** silently use the comment as the rule statement, merge comment and code into one rule, or ignore the contradiction.

## 5. Duplicate vs Contradictory Multi-Layer Enforcement

The same business rule is often enforced in multiple places (UI validation, service layer, database constraint). This requires careful judgment:

**Merge into one rule with multiple evidence entries when:**
- The condition, threshold, and outcome are semantically identical across layers
- Differences are purely technical (error message format, exception type) not behavioral

**Keep as separate, bidirectionally conflict-linked rules when:**
- Thresholds or conditions differ between layers (e.g., UI allows 100 characters but DB column is 80)
- One layer enforces a stricter or different version of the rule
- One enforcement exempts a population the other does not (e.g., one program exempts managers, another applies universally)
- Behavior on violation differs in business-meaningful ways (one rejects, another truncates)
- Two programs/modules enforce the same business concept with different parameters, even if possibly intentional

**Classification test:** If a business stakeholder reading both rules would ask "which one is correct?" or if a scenario exists where both rules execute and produce different outcomes for the same input, they are conflicts requiring `conflicting_rule_ids`. Possibly-intentional layered differences are STILL conflicts — mark them `needs_review` with an open question explaining the possible design rationale, but the structural conflict link is mandatory.

**`conflicting_rule_ids` vs `related_rule_ids` — decision boundary:**
- `conflicting_rule_ids`: same business concept (same entity + field/action) where subject, condition, threshold, or outcome differs. Bidirectional and mandatory whenever a discrepancy exists.
- `related_rule_ids`: different business concepts that merely reference the same entity or shared term. Example: "customer must be active to get a quote" and "customer must be active to file a claim" — same precondition, different business actions. Never use `related_rule_ids` or open-questions as a substitute for a structural conflict link.

**Document the pattern:** Note in both conflicting rules why they are linked and what the observable business behavior would be (which enforcement wins at runtime).

**Promotion rule:** If an open-question entry identifies cross-location enforcement divergence between two rules that are both extracted, those rules MUST have bidirectional `conflicting_rule_ids`. If only one location is extracted, extract the other as a separate rule, then add the conflict link. An open-question is complementary documentation — never a replacement for the structural link.

## 6. Generated Code

Code produced by generators, scaffolding tools, or build systems is typically excluded because:
- It is not a primary source of business logic
- It will be regenerated from its true source (templates, models, schemas)
- Extracting rules from it produces duplicates of rules already found in the generator input

**Detection markers:** `@Generated`, `// DO NOT EDIT`, `auto-generated`, build output paths, minified/bundled files with source map references, consistent mechanical formatting patterns.

**Exception:** If generated code has been manually modified (evident from version control or inconsistent style), treat the modified portions as analyzed source and note the generation origin.

## 7. Vendored and Third-Party Code

Libraries copied into the repository (vendor directories, shaded/shadowed dependencies) are excluded unless they have been modified to implement project-specific business logic.

**Detection:** `vendor/`, `third_party/`, `lib/` directories containing external packages; license files indicating foreign origin; version markers.

## 8. Oversized Files

Files too large for a single analysis pass (typically >2000 lines):

- Subdivide by logical regions: classes, function groups, sections delimited by comments.
- Maintain one coverage record per physical file.
- Track which logical regions have been analyzed.
- Business rules may span region boundaries — cross-reference when a rule's evidence spans regions.

## 9. Encoding and Character Set Issues

- Attempt UTF-8 first; fall back to Latin-1 (ISO 8859-1) for files that fail.
- For mainframe-origin sources transferred from EBCDIC: note encoding in coverage, process readable content, flag undecodable sections.
- Report undecodable files as coverage findings with `exclusion_reason.class = "binary"` and detail noting the encoding problem.
- Never crash on encoding errors — report and continue.

## 10. Monorepo Scoping

When the target is a subtree within a larger repository:
- Record the scope in `manifest.json` (`project.monorepo_scope`).
- All paths remain relative to the repository root, not the subtree.
- Files outside the scope get `exclusion_reason.class = "out_of_scope"`.
- Cross-references to code outside the scope are noted as external dependencies in `integrations.md`, not mined for rules.

## 11. Framework-Default Configuration as Rules

Framework conventions and default settings often look like business rules but are merely infrastructure:

**Exclude (framework default — not business logic):**
- Default session timeout, thread pool size, connection limits
- Auto-configured security headers with no project-specific customization
- Standard serialization format, date format, or locale settings
- Default pagination size or retry count

**Include (business policy expressed through configuration):**
- Password complexity requirements configured in a security module
- Business-specific rate limits (e.g., "max 3 password attempts")
- Domain-specific timeout policies (e.g., "payment session expires after 15 minutes")
- Custom validation rules defined in configuration files

**Decision test:** If the value were changed or removed, would the business behavior change in a way stakeholders care about? If only developer ergonomics or performance characteristics change → plumbing.

## 12. Cross-Cutting Rule Attribution

Logic like authorization middleware, audit logging with business conditions, or shared validation utilities cuts across domains. Failure modes:
- **Over-duplication:** recording the same cross-cutting rule in every domain that invokes it.
- **Under-attribution:** assigning a shared rule to only one domain arbitrarily.

**Handling:**
- Place genuinely cross-cutting rules (those not owned by any single domain) in the `cross-cutting/` output directory with their own `rules.json`.
- If the rule logically belongs to one domain but is consumed by others, own it in that domain and reference it from other domains' `integrations.md`.
- Never duplicate the same rule ID across domains — each rule has exactly one home.
