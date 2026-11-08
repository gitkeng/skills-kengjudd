#!/usr/bin/env bash
# Seeds the empty eval workspace with a small synthetic git repository:
# one baseline commit, then two unrelated uncommitted changes (a bug fix and a
# README edit) plus one untracked file, so a correct run proposes separate
# commits and stops for approval. Invented content only.
set -euo pipefail
git init -q -b main
git config user.email "eval@example.invalid"
git config user.name "Eval Fixture"
mkdir -p src
cat > src/pricing.py <<'PY'
def discount(total: float, member: bool) -> float:
    """Return the discounted total."""
    rate = 0.1 if member else 0.0
    return total - total * rate
PY
cat > README.md <<'MD'
# Pricing service (fixture)

Small example used only for tests.
MD
git add -A
git commit -q -m "Initial pricing module"
# change 1: bug fix in src/pricing.py (round to satang)
cat > src/pricing.py <<'PY'
def discount(total: float, member: bool) -> float:
    """Return the discounted total, rounded to two decimals."""
    rate = 0.1 if member else 0.0
    return round(total - total * rate, 2)
PY
# change 2: unrelated documentation edit
cat >> README.md <<'MD'

## Usage

Call `discount(total, member)`; members get 10% off.
MD
# untracked: a new test file
mkdir -p tests
cat > tests/test_pricing.py <<'PY'
from src.pricing import discount

def test_member_discount_rounds():
    assert discount(99.99, True) == 89.99
PY
