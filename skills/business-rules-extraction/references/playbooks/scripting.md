# Scripting Playbook

Stack-specific extraction guidance for Python, Ruby, PHP, JavaScript, and TypeScript.

## Detection Signals

- File extensions: `.py`, `.rb`, `.php`, `.js`, `.ts`, `.jsx`, `.tsx`, `.mjs`, `.cjs`
- Package manifests: `package.json`, `requirements.txt`, `Pipfile`, `pyproject.toml`, `Gemfile`, `composer.json`
- Shebangs: `#!/usr/bin/env python3`, `#!/usr/bin/env node`, `#!/usr/bin/env ruby`
- Framework markers: `manage.py` (Django), `config/routes.rb` (Rails), `artisan` (Laravel), `next.config.*`

## Dependency Signals

- **Import/require graphs:** `import`/`from...import` (Python), `require`/`import` (JS/TS), `require` (Ruby), `use`/`require_once` (PHP) reveal module dependencies.
- **Package structure:** `__init__.py` (Python packages), directory-based routing (Next.js, Nuxt), autoloading namespaces (PHP/Composer) indicate domain boundaries.
- **Configuration-driven routing:** Route files often enumerate all entry points (`urls.py`, `routes.rb`, Express routers, Laravel route files).

## Mining Strategy

Prefer **top-down** for web-centric scripting stacks: start from route definitions and entry points, follow request flow through middleware/decorators into handler logic. For data-heavy applications, supplement with bottom-up from schema/model definitions.

### Python

- **Django models:** Field definitions with validators, `Meta` constraints, `clean()` methods → validation/data_integrity.
- **Decorators:** `@login_required`, `@permission_required`, custom decorators with conditions → access_control.
- **Pydantic/attrs/dataclass validators:** Field validators and model validators → validation rules.
- **Celery/APScheduler tasks:** Scheduled and triggered background work → batch/process_workflow.
- **Assert statements and `raise ValueError/TypeError`:** Precondition checks → constraints (distinguish business from defensive programming).
- **Django signals, custom event systems:** Post-save/pre-delete handlers → action_enabler rules.

### Ruby (Rails)

- **ActiveRecord validations:** `validates :field, presence: true, numericality: {greater_than: 0}` → validation rules.
- **Callbacks:** `before_save`, `after_create` with business conditions → action_enabler rules.
- **Scopes with business conditions:** `scope :active, -> { where(status: 'active') }` → inference/fact rules.
- **Pundit/CanCanCan policies:** Authorization logic → access_control rules.
- **State machines (AASM, etc.):** Explicit state transitions with guards → process_workflow rules.
- **ActiveJob/Sidekiq workers:** Background processing → batch rules.

### PHP (Laravel/Symfony)

- **Form Requests with `rules()`:** Validation arrays → validation rules.
- **Eloquent mutators/casts, model events:** Data transformation and lifecycle logic → business rules.
- **Policies and Gates:** `$this->authorize()`, Gate definitions → access_control rules.
- **Middleware with business logic:** Beyond auth (rate limiting by business tier, maintenance mode by role) → constraints.
- **Queued jobs and scheduled commands:** `schedule()` definitions → batch/process_workflow rules.
- **Blade directives with `@can`/`@if` business conditions:** UI-layer visibility rules.

### JavaScript/TypeScript

- **Validation libraries (Joi, Zod, Yup):** Schema definitions → validation rules with clear structure.
- **Express/Fastify middleware:** Auth checks, rate limits, business guards → access_control/constraint rules.
- **React/Vue/Angular form validation:** Component-level validation logic → UI layer rules (merge/conflict check with API validation).
- **State management (Redux reducers, Vuex mutations):** State transition conditions → process_workflow rules.
- **Serverless function handlers:** Each handler is often one business capability entry point.
- **TypeScript type guards and discriminated unions:** Type narrowing with business meaning → inference/decision rules.
- **Next.js/Nuxt middleware and API routes:** Request-level auth and business guards.

## Dynamic Language Challenges

- **Duck typing:** Rule evidence may be less explicit than in statically typed languages; look for runtime type checks (`isinstance`, `typeof`, `is_a?`) as business condition signals.
- **Metaprogramming:** `method_missing` (Ruby), `__getattr__` (Python), `Proxy` (JS) may hide business logic; follow the dynamic dispatch to its implementation.
- **Configuration as code:** Business rules defined in data structures (route tables, validation schemas, permission maps) are still rules — classify by the layer where they are enforced.
- **Monkey patching:** Modifications to existing classes/modules may override or add business rules; check for this pattern and document the override.

## Definition-Use Tracing

For every threshold, constant, or flag referenced at an enforcement site, trace backward to the definition: environment variable, config file, constants module, enum, or settings object. Include the definition source as evidence when it supplies the concrete value. When multiple modules enforce the same concept (e.g., middleware and handler both check the same limit), compare values — identical enforcement merges; differing thresholds become conflict-linked rules.

## Evidence Layer Mapping

| Source Type | Layer |
|------------|-------|
| Service/handler/controller logic | `code` |
| Model definitions and validators | `code` |
| SQL migrations, schema definitions | `sql` |
| Database constraints in migration files | `db_constraint` |
| Background jobs, scheduled tasks | `batch` |
| Event handlers, message queues | `workflow` |
| Form validation, UI components | `ui` |
| Config files, environment variables in conditionals | `config` |
| Rule engine definitions (JSON rules, decision tables) | `rules_engine` |
