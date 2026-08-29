# Rule Schema Reference

Canonical specification for every `domains/<slug>/rules.json` file.

## File Structure

```json
{
  "schema_version": "1.0",
  "domain": "<slug>",
  "rules": [ /* rule objects */ ]
}
```

## Rule Record Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `id` | yes | string | Pattern `BR-<domain-slug>-<nnn>`. Globally unique, never reused within a run. |
| `name` | yes | string | Short descriptive name (2–120 characters). |
| `statement` | yes | string | One atomic plain-language business rule. No OR on conditions, no AND on actions. |
| `rule_type` | yes | enum | `fact`, `constraint`, `action_enabler`, `inference`, or `computation`. |
| `category` | conditional | enum | One of: `validation`, `calculation`, `decision`, `process_workflow`, `data_integrity`, `access_control`. Required when `rule_type` is not `fact`. Must be absent/null when `rule_type` is `fact`. |
| `acceptance_criteria` | yes | array | One or more Given/When/Then objects. |
| `evidence` | yes | array | One or more source evidence entries (minimum 1). |
| `business_context` | yes | array | One or more anchors into domain documentation. |
| `data_elements` | yes | array | Business terms used, with glossary links. May be empty `[]` only if no domain terms apply. |
| `relationships` | yes | object | Cross-references to other rules. |
| `confidence` | yes | object | Confidence assessment. |
| `review` | yes | object | SME review tracking. |
| `criticality` | no | object | Optional business criticality. |
| `applicability` | no | object | Optional dead-code/active state. |
| `open_questions` | no | array | Unresolved questions about this rule. |

## Field Detail

### acceptance_criteria[]

Each object has exactly three string fields: `given`, `when`, `then`. Write from the business perspective — the criteria must be verifiable by an SME without reading code.

**Canonical evidence-verification pattern (non-vacuous):**

```json
{
  "given": "A customer account exists with status active",
  "when": "The customer submits a withdrawal exceeding the daily limit",
  "then": "The transaction is rejected with error code LIMIT_EXCEEDED"
}
```

**Fact-type rules:** Facts still require at least one acceptance criterion. Use the evidence-verification pattern — Given establishes observable state, When specifies an inspection or query, Then states the verifiable truth:

```json
{
  "given": "The customer data model exists",
  "when": "The maximum length of the email field is inspected",
  "then": "The maximum length is 255 characters"
}
```

**Multi-scenario guidance:** Rules with boundary conditions should have multiple G/W/T entries covering the positive case, negative case, and boundary:

```json
[
  {
    "given": "A customer has a daily withdrawal limit of 5000",
    "when": "The customer requests a withdrawal of 4000",
    "then": "The transaction is approved"
  },
  {
    "given": "A customer has a daily withdrawal limit of 5000",
    "when": "The customer requests a withdrawal of 5001",
    "then": "The transaction is rejected with reason LIMIT_EXCEEDED"
  },
  {
    "given": "A customer has a daily withdrawal limit of 5000",
    "when": "The customer requests a withdrawal of exactly 5000",
    "then": "The transaction is approved (limit is inclusive)"
  }
]
```

**Anti-patterns (do NOT write these):**

| Bad | Problem | Corrected |
|-----|---------|-----------|
| Given the service calls the DAO layer | Implementation leakage — references code structure | Given a customer record exists in the system |
| Then the correct result is returned | Unverifiable — what is "correct"? | Then the calculated tax is 15% of the subtotal |
| Given A and B and C exist | Compound Given smuggling multiple preconditions | Split into separate acceptance criteria |
| When anything happens | Vacuous — no testable trigger | When the monthly statement is generated |

### evidence[]

```json
{
  "file": "src/services/withdrawal-service.js",
  "line_start": 142,
  "line_end": 158,
  "snippet": "if (amount > customer.dailyLimit) {\n  throw new LimitExceededError(...);\n}",
  "layer": "code"
}
```

- `file`: forward-slash repository-relative path.
- `line_start`, `line_end`: 1-based inclusive line range.
- `snippet`: verbatim source text from within that range (whitespace variations tolerated by validator).
- `layer`: one of `code`, `sql`, `db_constraint`, `batch`, `workflow`, `ui`, `config`, `rules_engine`.

Multiple evidence entries for one rule indicate the same business logic enforced at multiple layers — this is correct and expected for merged multi-layer rules.

### business_context[]

```json
{
  "file": "domains/payments/features.md",
  "anchor": "## Daily Withdrawal Limits",
  "kind": "feature"
}
```

- `file`: path within the output tree (forward-slash relative to output root).
- `anchor`: section heading or identifier in that file.
- `kind`: `feature` or `workflow`.

Every rule must have at least one context anchor. SMEs navigate process-first, not file-first.

### data_elements[]

```json
{
  "term": "Daily Limit",
  "glossary_anchor": "glossary.md#daily-limit"
}
```

Links the business terms this rule uses to their glossary definitions.

### relationships

```json
{
  "related_rule_ids": ["BR-payments-004"],
  "duplicate_rule_ids": [],
  "conflicting_rule_ids": ["BR-accounts-012"]
}
```

All three arrays are required (may be empty). Every ID listed must exist in some domain's `rules.json`. Conflict links must be bidirectional: if A lists B as conflicting, B must list A.
**Field semantics (decision boundary):**
- `conflicting_rule_ids` — Rules addressing the SAME business concept (same entity + field/action) where subject scope, condition, threshold, or outcome DIFFERS. Mandatory whenever a discrepancy exists between two enforcement points of the same concept, even if the difference is possibly intentional. Set `needs_review` and add an open question explaining the possible rationale, but the structural link is non-negotiable.
- `related_rule_ids` — Rules addressing DIFFERENT business concepts that share an entity or term but do not conflict. Example: two rules both reference "customer status" but govern different business actions (quoting vs claims). Never use `related_rule_ids` as a catch-all for uncertain conflicts — when in doubt, use `conflicting_rule_ids`.
- `duplicate_rule_ids` — Exact semantic duplicates (same concept, same enforcement, different locations) that should be merged but have been retained for traceability.
**Anti-pattern:** Placing a discrepancy in `open_questions` or `related_rule_ids` without a corresponding `conflicting_rule_ids` entry. Open questions and related links are supplemental documentation; they never substitute for structural conflict linking.

### confidence

```json
{
  "level": "high",
  "justification": "Explicit conditional with clear business error message and matching DB constraint"
}
```

- `level`: `high`, `medium`, or `low`.
- Automatic status behavior: confidence below `high` sets `review.status` to `needs_review`.

### review

```json
{
  "status": "extracted",
  "reviewer": null,
  "reviewed_on": null
}
```

- `status`: `extracted`, `needs_review`, `validated`, `rejected`, or `obsolete`.
- `reviewer`: null until an SME acts; then name or identifier string.
- `reviewed_on`: null or ISO 8601 date string.
- Initial extraction sets `extracted` (high confidence) or `needs_review` (medium/low).

### criticality (optional)

```json
{
  "level": "core",
  "basis": "Regulatory requirement — transaction limits mandated by banking authority"
}
```

- `level`: `core`, `supporting`, or `peripheral`.
- `basis`: brief justification for the assigned level.

### applicability (optional)

```json
{
  "state": "active",
  "justification": "Called from active transaction processing flow"
}
```

- `state`: `active`, `dead`, or `uncertain`.
- Use this to explicitly handle dead code: a rule found only in unreachable logic gets `dead` state and is flagged rather than presented as an active business rule.

### open_questions[] (optional)

```json
["Is the 10000 limit in cents or dollars? No unit annotation found in code or schema."]
```

Array of question strings for SME clarification.

## ID Stability and Rerun Policy

Within a single extraction run, IDs are globally unique and never reused.

On rerun against the same repository:
1. Match existing rules by evidence file/line overlap AND statement semantic similarity.
2. Matched rules retain their original IDs.
3. New rules receive IDs numbered above the prior per-domain maximum.
4. Rules present in the prior run but no longer found in source are marked `obsolete` (status) and retained in the catalog with their original IDs.

This policy is guidance for the executing agent — no automated ID-matching code is shipped.

## Complete Example

```json
{
  "schema_version": "1.0",
  "domain": "payments",
  "rules": [
    {
      "id": "BR-payments-001",
      "name": "Daily Withdrawal Limit Enforcement",
      "statement": "A withdrawal transaction is rejected when the requested amount exceeds the customer's configured daily withdrawal limit.",
      "rule_type": "constraint",
      "category": "validation",
      "acceptance_criteria": [
        {
          "given": "A customer has a daily withdrawal limit of 5000",
          "when": "The customer requests a withdrawal of 6000",
          "then": "The system rejects the transaction with reason LIMIT_EXCEEDED"
        }
      ],
      "evidence": [
        {
          "file": "src/services/withdrawal-service.js",
          "line_start": 142,
          "line_end": 158,
          "snippet": "if (amount > customer.dailyLimit) {\n  throw new LimitExceededError(amount, customer.dailyLimit);\n}",
          "layer": "code"
        },
        {
          "file": "db/constraints.sql",
          "line_start": 34,
          "line_end": 36,
          "snippet": "ALTER TABLE transactions ADD CONSTRAINT chk_daily_limit\n  CHECK (amount <= (SELECT daily_limit FROM accounts WHERE id = account_id));",
          "layer": "db_constraint"
        }
      ],
      "business_context": [
        {
          "file": "domains/payments/features.md",
          "anchor": "## Daily Withdrawal Limits",
          "kind": "feature"
        }
      ],
      "data_elements": [
        {"term": "Daily Withdrawal Limit", "glossary_anchor": "glossary.md#daily-withdrawal-limit"},
        {"term": "Transaction Amount", "glossary_anchor": "glossary.md#transaction-amount"}
      ],
      "relationships": {
        "related_rule_ids": ["BR-payments-002"],
        "duplicate_rule_ids": [],
        "conflicting_rule_ids": []
      },
      "confidence": {
        "level": "high",
        "justification": "Explicit conditional in code with matching database constraint"
      },
      "review": {
        "status": "extracted",
        "reviewer": null,
        "reviewed_on": null
      },
      "criticality": {
        "level": "core",
        "basis": "Financial transaction control — regulatory compliance"
      },
      "applicability": {
        "state": "active",
        "justification": "Called from active withdrawal processing endpoint"
      },
      "open_questions": []
    }
  ]
}
```
