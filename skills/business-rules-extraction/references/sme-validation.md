# SME Validation Reference

Protocol for conducting stakeholder review sessions and managing the validation lifecycle.

## Review Workbook

The primary artifact for SME validation is `review-workbook.csv`:

```csv
rule_id,domain,statement,question,disposition,comments
BR-payments-001,payments,"A withdrawal is rejected when amount exceeds daily limit",Is this per calendar day or rolling 24h?,,
BR-payments-002,payments,"Late fee is calculated as 1.5% of outstanding balance",What is the regulatory basis for this percentage?,,
```

**Columns:**
- `rule_id` — stable identifier linking back to `rules.json`
- `domain` — domain slug for context
- `statement` — the extracted rule in plain language
- `question` — generated from `open_questions` or low/medium confidence justification; blank for high-confidence rules without questions
- `disposition` — blank; SME fills with: `confirm` (rule is accurate as stated), `modify` (rule needs rewording — see comments), `reject` (not a real business rule)
- `comments` — blank; SME provides corrections, context, or clarification

**Generation rules:**
- Include every extracted rule regardless of confidence
- Sort by domain, then by rule ID within domain
- Pre-fill `question` from the rule's `open_questions` array; if multiple questions exist, join with semicolons
- For rules with confidence `medium` or `low`, append the confidence justification as a question if no explicit question exists

## Validation Session Protocol

### Before the Session

1. **Prepare materials:** Generate the review workbook, print or share per-domain `business-rules.md` for reference, and prepare `open-questions.md` as the discussion agenda.
2. **Select participants:** Domain experts who own or operate the business processes — not developers (unless they are also the domain experts).
3. **Scope each session:** One domain per session (two at most for small domains). Sessions exceeding 90 minutes lose effectiveness.
4. **Pre-read:** Send the domain's `overview.md` and `business-rules.md` to participants 2–3 days in advance.

### During the Session

1. **Orientation (5 min):** Explain the three dispositions (confirm/modify/reject) and that the goal is accuracy of business intent, not code review.
2. **Walk through rules by feature grouping:** Use `business-rules.md` organization. For each rule:
   - Read the statement aloud
   - Ask: "Is this accurate? Is anything missing or overstated?"
   - Record disposition and any corrections in the workbook
3. **Address open questions:** Use `open-questions.md` as a checklist. Record answers as comments against the relevant rules.
4. **Capture new rules:** SMEs often identify rules the code implies but does not explicitly enforce ("we always do X even though the system doesn't check"). Record these as new candidate rules with `confidence.level = "low"` and `confidence.justification = "SME-reported; no code evidence found"`.
5. **Close (5 min):** Summarize changes and identify follow-up items.

### After the Session

1. **Update review status:**
   - `confirm` → set `review.status = "validated"`, `review.reviewer`, `review.reviewed_on`
   - `modify` → update `statement` and/or `acceptance_criteria`, set status to `validated`
   - `reject` → set `review.status = "rejected"` with reviewer/date
2. **Process new candidates:** Add SME-reported rules to `rules.json` with appropriate evidence (may be empty if purely oral knowledge — document this).
3. **Regenerate affected outputs:** Re-render `business-rules.md` from updated `rules.json`. Rerun validator.
4. **Archive the completed workbook:** Store the filled CSV as session evidence.

## Status Lifecycle

```
extracted ──→ needs_review ──→ validated
                   │                │
                   ├──→ rejected    ├──→ obsolete
                   │                │
                   └──→ validated   └──→ needs_review (if re-extraction finds changes)
```

- `extracted`: initial state for high-confidence rules
- `needs_review`: initial state for medium/low confidence; also set when re-extraction detects changes to a previously validated rule
- `validated`: SME confirmed the rule is accurate
- `rejected`: SME determined this is not a real business rule
- `obsolete`: rule no longer present in source (rerun policy)

## Incremental Validation

For large systems, validate incrementally by domain priority:
1. Start with core domains (highest business criticality or change frequency)
2. Use the workbook's domain column to filter sessions
3. Track validation progress in the manifest: compare `review.status` distribution per domain

## Handling Disagreements

When SMEs disagree about a rule:
- Record both perspectives in the rule's `open_questions`
- Set status to `needs_review` with a comment noting the disagreement
- Escalate to a domain owner or process owner for resolution
- Never resolve business disagreements by code interpretation alone — code may implement an incorrect understanding

## Workbook Export Variants

The standard CSV format works in any spreadsheet tool. For organizations needing richer formats:
- The `rules.json` canonical format supports direct import into requirements management tools
- The Gherkin export provides executable acceptance criteria for validation in test frameworks
- The DMN export provides decision tables reviewable in business rule management systems
