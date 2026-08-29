# Rule Taxonomy Reference

## Semantic Types (rule_type)

Derived from established classification (von Halle; Wiegers & Beatty, Software Requirements 3rd ed. ch. 9; Business Rules Group GUIDE Report):

| Type | Definition | Example Pattern |
|------|-----------|-----------------|
| `fact` | A stable truth about business entities or their relationships. No condition/action — just what IS. | "A customer has exactly one primary account." |
| `constraint` | A condition that must hold; violations are prevented or flagged. | "An order total must not exceed the customer credit limit." |
| `action_enabler` | A condition that, when met, permits or triggers an action. | "When an invoice is 30 days past due, a reminder notice is sent." |
| `inference` | A condition that derives new information from existing facts. | "A customer who has not purchased in 12 months is classified as inactive." |
| `computation` | A defined formula or algorithm producing a calculated value. | "Shipping cost equals base rate plus weight multiplied by the per-kilogram surcharge." |

## Practical Categories (category)

The category facet is a pragmatic design choice of this specification for organizing rules by operational concern. It is not drawn from external literature.

| Category | Scope |
|----------|-------|
| `validation` | Input correctness, format, range, and mandatory-field checks. |
| `calculation` | Formulas, derived values, aggregations, pricing, scoring. |
| `decision` | Branching logic that selects a path, classification, or outcome. |
| `process_workflow` | Sequencing, state transitions, approvals, escalations. |
| `data_integrity` | Referential integrity, uniqueness, cascade, and consistency rules beyond simple input validation. |
| `access_control` | Authorization, role-based permissions, data visibility, ownership checks. |

## Validity Matrix

Category is required when `rule_type` is not `fact`. Category must be absent/null when `rule_type` is `fact`. All non-fact type × category combinations are legal. Not every pairing is equally common; the examples below illustrate both natural and less common applications.

| | validation | calculation | decision | process_workflow | data_integrity | access_control | no category |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **fact** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| **constraint** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **action_enabler** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **inference** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **computation** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

## Worked Examples — Every Legal Cell

### fact × (no category)
"Each purchase order is associated with exactly one supplier." — Captures a structural business truth. Normally routed to the glossary; promoted to a BR record only if an SME would need to confirm or could dispute it.

### constraint × validation
"A customer email address must match a valid email format before account creation is permitted."

### constraint × calculation
"The calculated discount percentage must not exceed 40% of the item base price."

### constraint × decision
"A loan application must be declined when the applicant debt-to-income ratio exceeds 0.43."

### constraint × process_workflow
"A purchase order cannot transition to Shipped status until the payment status is Confirmed."

### constraint × data_integrity
"Deleting a department record is prevented while active employees remain assigned to it."

### constraint × access_control
"Only users with the Approver role may authorize expenditures above the standard threshold."

### action_enabler × validation
"When all mandatory profile fields pass validation, the Submit button becomes active."

### action_enabler × calculation
"When the cart total exceeds the free-shipping threshold, shipping cost is set to zero."

### action_enabler × decision
"When a claim amount is below the auto-approval ceiling, the claim is approved without manual review."

### action_enabler × process_workflow
"When all required approvals are collected, the contract advances to the Execution stage."

### action_enabler × data_integrity
"When a parent account is closed, all child sub-accounts are archived with a closure reference."

### action_enabler × access_control
"When a user completes identity verification, elevated-privilege operations are unlocked for the session."

### inference × validation
"A postal code that does not match any known region pattern is flagged as potentially invalid."

### inference × calculation
"A customer whose rolling 12-month spend exceeds the tier threshold is classified as Premium."

### inference × decision
"An order containing items from multiple warehouses is flagged for split-shipment routing."

### inference × process_workflow
"A support ticket unresolved for 48 hours is inferred as escalation-eligible."

### inference × data_integrity
"A product record whose last inventory count is older than 90 days is marked as stale."

### inference × access_control
"A session idle for more than 30 minutes is inferred as abandoned and access is revoked."

### computation × validation
"The computed check digit of a national identification number must equal the final digit submitted."

### computation × calculation
"Monthly interest is computed as principal multiplied by annual rate divided by twelve."

### computation × decision
"The risk score is computed from weighted factors; if the score exceeds the threshold, manual review is required."

### computation × process_workflow
"The estimated delivery date is computed from warehouse processing time plus carrier transit days; this date drives the fulfillment stage deadline."

### computation × data_integrity
"The order line total is computed as quantity multiplied by unit price; this computed value must equal the stored line_total field."

### computation × access_control
"The remaining API quota is computed as the plan limit minus requests consumed in the current window; when the result reaches zero, further requests are denied."

## Decision Guide

1. **Identify the type first** by asking: does this rule state what IS (fact), what must NOT happen (constraint), what CAN/DOES happen when a condition is met (action_enabler), what new knowledge is derived (inference), or what value is calculated (computation)?
2. **Then assign the category** by asking: what operational concern does this rule serve? Input correctness → validation. Formula or derived value → calculation. Branching/routing → decision. Sequencing/state → process_workflow. Referential/consistency → data_integrity. Who-can-do-what → access_control.
3. **If two categories seem equally applicable**, choose the one that best describes the rule's PRIMARY business purpose, not its implementation mechanism.

**Inference vs computation tie-breaker:** If the rule produces a new boolean/categorical classification from existing data → `inference`. If it produces a numeric/date/string value via a formula or algorithm → `computation`. Example: "Customer with spend > 10K is classified Premium" → inference (derives a category). "Loyalty points = purchase_total × 0.01" → computation (calculates a value).

## Literature Citations

- Business Rules Group. "Defining Business Rules — What Are They Really?" GUIDE Business Rules Project, Final Report, 3rd ed. https://www.businessrulesgroup.org/first_paper/BRG-whatisBR_3ed.pdf
- Wiegers, K. & Beatty, J. Software Requirements, 3rd ed., ch. 9. 2013.
- OMG. Semantics of Business Vocabulary and Business Rules (SBVR) 1.5. https://www.omg.org/spec/SBVR/1.5/About-SBVR
