#!/usr/bin/env bash
# Seeds the empty eval workspace with a small synthetic Python service
# (invented content only): an orders module carrying a few business rules,
# an auth handler with a deliberate missing-CSRF check, a duplicated helper,
# tests, a migration, a Dockerfile and a CI workflow — enough surface for
# every codebase-analysis phase to have something to say.
set -euo pipefail
mkdir -p src/orders src/auth tests migrations .github/workflows
cat > README.md <<'MD'
# Meeting-room orders service (fixture)

Synthetic example used only for tests. Flask-style HTTP service that sells
meeting-room bookings; nothing here is real.

Run: `python -m src.app` — Tests: `pytest`
MD
cat > requirements.txt <<'TXT'
flask==2.3.3
sqlalchemy==2.0.23
pytest==7.4.3
TXT
cat > Dockerfile <<'DF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src ./src
CMD ["python", "-m", "src.app"]
DF
cat > .github/workflows/ci.yml <<'YML'
name: ci
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest -q
YML
cat > migrations/001_init.sql <<'SQL'
CREATE TABLE customers (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  is_member BOOLEAN NOT NULL DEFAULT 0
);
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  room TEXT NOT NULL,
  starts_at TEXT NOT NULL,
  total_cents INTEGER NOT NULL CHECK (total_cents >= 0),
  status TEXT NOT NULL DEFAULT 'pending'
);
SQL
cat > src/__init__.py <<'PY'
PY
cat > src/orders/__init__.py <<'PY'
PY
cat > src/auth/__init__.py <<'PY'
PY
cat > src/util.py <<'PY'
"""Small helpers. Note: cents_to_text is duplicated in orders/service.py."""


def cents_to_text(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d} THB"


def parse_iso(value: str):
    from datetime import datetime
    return datetime.fromisoformat(value)
PY
cat > src/orders/models.py <<'PY'
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Customer:
    id: int
    email: str
    is_member: bool = False


@dataclass
class Order:
    id: int
    customer: Customer
    room: str
    starts_at: datetime
    total_cents: int
    status: str = "pending"
    notes: list[str] = field(default_factory=list)
PY
cat > src/orders/service.py <<'PY'
"""Order rules for meeting-room bookings."""
from datetime import datetime, timedelta

from .models import Customer, Order

MINIMUM_TOTAL_CENTS = 20_000          # 200.00 THB
MEMBER_DISCOUNT_RATE = 0.10
MAX_ADVANCE_DAYS = 30
CANCEL_CUTOFF_HOURS = 2


class OrderError(Exception):
    pass


def cents_to_text(cents: int) -> str:            # duplicated from src/util.py
    return f"{cents // 100}.{cents % 100:02d} THB"


def price_for(customer: Customer, list_price_cents: int) -> int:
    """Members get 10% off the list price."""
    if customer.is_member:
        return round(list_price_cents * (1 - MEMBER_DISCOUNT_RATE))
    return list_price_cents


def place_order(customer: Customer, room: str, starts_at: datetime, list_price_cents: int, now: datetime) -> Order:
    total = price_for(customer, list_price_cents)
    if total < MINIMUM_TOTAL_CENTS:
        raise OrderError("order below minimum total")
    if starts_at > now + timedelta(days=MAX_ADVANCE_DAYS):
        raise OrderError("bookings open at most 30 days ahead")
    if starts_at < now:
        raise OrderError("cannot book in the past")
    return Order(id=0, customer=customer, room=room, starts_at=starts_at, total_cents=total)


def cancel_order(order: Order, now: datetime) -> Order:
    """Cancellation is free until two hours before the booking starts."""
    if order.status == "cancelled":
        return order
    if order.starts_at - now < timedelta(hours=CANCEL_CUTOFF_HOURS):
        raise OrderError("too late to cancel")
    order.status = "cancelled"
    return order
PY
cat > src/auth/handler.py <<'PY'
"""Session handling. The form handlers below never check a CSRF token."""
import hashlib
import os

SESSIONS: dict[str, int] = {}


def login(email: str, password: str, users: dict[str, str]) -> str | None:
    digest = hashlib.sha256(password.encode()).hexdigest()   # unsalted hash
    if users.get(email) != digest:
        return None
    token = os.urandom(16).hex()
    SESSIONS[token] = hash(email)
    return token


def current_user(token: str | None) -> int | None:
    return SESSIONS.get(token or "")


def submit_form(token: str | None, form: dict) -> bool:
    """State-changing POST handler; accepts any origin (no CSRF check)."""
    if current_user(token) is None:
        return False
    return bool(form)
PY
cat > src/app.py <<'PY'
"""HTTP entry points (framework calls stubbed so the module imports without Flask)."""
from datetime import datetime

from .auth.handler import submit_form, login
from .orders.models import Customer
from .orders.service import place_order, cancel_order, OrderError

ROUTES = {}


def route(path):
    def deco(fn):
        ROUTES[path] = fn
        return fn
    return deco


@route("/login")
def login_view(form):
    return login(form.get("email", ""), form.get("password", ""), users={})


@route("/orders")
def create_order_view(token, form):
    if not submit_form(token, form):
        return {"error": "forbidden"}, 403
    customer = Customer(id=1, email=form["email"], is_member=form.get("member") == "1")
    try:
        order = place_order(customer, form["room"], datetime.fromisoformat(form["starts_at"]), int(form["price_cents"]), datetime.utcnow())
    except OrderError as exc:
        return {"error": str(exc)}, 400
    return {"total_cents": order.total_cents}, 201


@route("/orders/cancel")
def cancel_view(token, order, form):
    if not submit_form(token, form):
        return {"error": "forbidden"}, 403
    try:
        cancel_order(order, datetime.utcnow())
    except OrderError as exc:
        return {"error": str(exc)}, 400
    return {"status": order.status}, 200


if __name__ == "__main__":
    print(sorted(ROUTES))
PY
cat > tests/test_orders.py <<'PY'
from datetime import datetime, timedelta

import pytest

from src.orders.models import Customer
from src.orders.service import place_order, cancel_order, OrderError

NOW = datetime(2026, 1, 1, 9, 0)


def test_member_discount_applied():
    order = place_order(Customer(1, "a@example.invalid", True), "R1", NOW + timedelta(days=1), 30_000, NOW)
    assert order.total_cents == 27_000


def test_below_minimum_rejected():
    with pytest.raises(OrderError):
        place_order(Customer(1, "a@example.invalid", False), "R1", NOW + timedelta(days=1), 10_000, NOW)


def test_cancel_too_late():
    order = place_order(Customer(1, "a@example.invalid", False), "R1", NOW + timedelta(hours=1), 30_000, NOW)
    with pytest.raises(OrderError):
        cancel_order(order, NOW)
PY
git init -q -b main
git -c user.email=eval@example.invalid -c user.name="Eval Fixture" add -A
git -c user.email=eval@example.invalid -c user.name="Eval Fixture" commit -q -m "Initial fixture service"
