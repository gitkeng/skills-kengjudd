---
type: llm
focus: last_message
---

PASS if the reply proposes at least two separate commits — one covering the
fix in src/pricing.py and one covering the README.md documentation change
(the new tests/test_pricing.py may ride with the fix or stand alone) — and
asks the user to approve before anything is committed.

FAIL if it proposes a single commit for everything, if it states that a
commit was already created, or if it ignores the untracked test file entirely.
