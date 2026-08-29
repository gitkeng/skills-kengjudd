# Playbook: TypeScript + React + Next.js Business Rules Extraction

## Project & Package Signals

- `tsconfig.json` → `strict`, `strictNullChecks`, `paths`, `baseUrl` reveal enforcement level and module aliasing.
- `package.json` → `dependencies` vs `devDependencies` distinguish runtime vs build-only libraries.
- Presence of `zod`, `yup`, `io-ts`, `joi`, `superstruct` signals runtime validation schemas.
- `next.config.js`/`next.config.mjs` → `rewrites`, `redirects`, `headers`, `env`, `serverComponentsExternalPackages`.
- Monorepo markers: `workspaces`, `turbo.json`, `nx.json` affect rule boundary tracing.

## Evidence-Layer Mapping

Every evidence entry requires a `layer` value from the schema enum. Map TypeScript/React/Next.js artifacts as follows:

| Schema `layer` | TypeScript / React / Next.js Artifacts |
|----------------|----------------------------------------|
| `code` | Server actions, route handlers, `getServerSideProps`, middleware logic, custom hooks, reducers, form validation callbacks, guard components, utility functions with business predicates |
| `sql` | Raw SQL in route handlers or server actions (`prisma.$queryRaw`, `knex.raw`, template SQL) |
| `db_constraint` | Prisma schema (`@unique`, `@default`, `@@index`, field types, relations), Drizzle schema definitions, migration files with CHECK/UNIQUE/FK constraints |
| `ui` | Controlled input validation (`onChange`/`onBlur`), form library resolver schemas (react-hook-form, formik), `disabled`/`required` attributes, conditional rendering guards, visibility predicates |
| `config` | Environment variables (`process.env.X`, `NEXT_PUBLIC_X`), constants files, feature flag definitions, `next.config.js` rewrites/redirects/headers, route matcher config |
| `workflow` | State machine transitions in reducers, middleware redirect chains, revalidation flows (`revalidatePath`/`revalidateTag`), layout-level auth gates applied to child routes |
| `batch` | Scheduled jobs (cron handlers), `generateStaticParams` build-time enumeration, ISR revalidation intervals, bulk processing endpoints |
| `rules_engine` | Zod/Yup/io-ts/Joi schema definitions with `.refine()`, `.transform()`, `.test()`, custom validator compositions, discriminated-union-driven decision tables |

## TypeScript Types Are Candidate Facts, Not Validation Proof

TypeScript `interface` and `type` declarations (including branded types, discriminated unions, template literal types, `as const` assertions, and generic constraints) describe compile-time shape expectations. They are **candidate facts** — evidence that a data model or enumeration exists — but they do NOT prove runtime enforcement. The type system is erased at build time.

- Extract type declarations as `rule_type: "fact"` candidates only.
- Promote to `constraint` or other non-fact types exclusively when a corresponding runtime enforcement artifact exists (Zod schema, server-side guard, DB constraint, middleware check).
- When a schema library infers types (`z.infer<typeof S>`), the schema is the authoritative evidence — extract from the schema definition, not the inferred type alias.

## Client/Server Threshold and Enforcement Differences

When the same business concept is enforced on both client and server:

- **Identical enforcement (same subject, condition, threshold, outcome):** Merge into one rule with multiple evidence entries spanning both locations. Use `layer: "ui"` for the client entry and the appropriate layer (`code`, `rules_engine`, `db_constraint`) for the server entry.
- **Different threshold, scope, or outcome:** Keep as **separate rules** with bidirectional `conflicting_rule_ids`. Each rule gets its own evidence. Add an `open_questions` entry explaining the divergence. The server-side rule is the authoritative enforcement; the client-side rule is UI-only.

Examples of bidirectional conflicts:
- Client validates max 100 characters; server validates max 80 characters → two rules, conflicting.
- Client allows guest checkout; server action rejects unauthenticated users → two rules, conflicting.
- Client-side form permits optional field; server schema requires it → two rules, conflicting.

## Compile-Time Types vs Runtime Schemas

| Artifact | Rule Signal | Extraction Guidance |
|----------|-------------|---------------------|
| `interface`, `type`, branded types | Shape constraints, optionality, enums, literal narrowing | Candidate `fact` only |
| Discriminated unions (`type: "admin" \| "guest"`) | Role/state machine encoding | `fact` unless transition logic enforces it at runtime |
| `as const` assertions | Frozen allowed value sets | `fact` (enumeration) |
| Generic constraints (`T extends { status: "active" }`) | Preconditions | `fact` unless runtime check accompanies |
| Zod `.refine()`, `.transform()` | Business predicates, cross-field deps, coercion | `constraint` / `computation` with `rules_engine` layer |
| Yup `.test()`, Joi `.custom()` | Custom validation predicates | `constraint` with `rules_engine` layer |
| Inferred types (`z.infer<typeof S>`) | Single source of truth | Extract from schema side, not the alias |

## React: Forms, Hooks, Reducers, Guards

### Forms
- Controlled inputs with validation in `onChange`/`onBlur` → field-level rules (`ui` layer).
- Form libraries (`react-hook-form`, `formik`) → resolver/validation schema is the rule source (`rules_engine` layer).
- `disabled`, `required`, conditional `render` → UI enforcement of eligibility/visibility rules (`ui` layer).

### Hooks
- Custom hooks returning `{ canX, isAllowed, hasPermission }` → authorization predicates (`code` layer).
- `useEffect` with guard clauses → side-effect preconditions (`code` layer).
- `useMemo`/`useCallback` with conditional logic → derived eligibility or computed state rules (`code` layer).

### Reducers
- `useReducer` action/state pairs → state machine transitions (`workflow` layer).
- Switch cases with guard conditions before state change → transition preconditions (`code` layer).
- Thrown errors or returned unchanged state → rejected transitions / invariants (`code` layer).

### Guards & Visibility
- Early returns in components → render guards (`ui` layer).
- Conditional JSX (`{condition && <X/>}`, ternaries) → visibility rules (`ui` layer).
- HOCs/wrappers (`withAuth`, `ProtectedRoute`) → access control boundaries (`code` layer).

## Next.js: Routing, Middleware, Server Actions, Boundaries

### App Router (`app/`)
- `layout.tsx` → shared constraints (auth checks, provider wrappers) applied to child routes (`workflow` layer).
- Route groups `(groupName)` → logical segmentation without URL impact (structural, not a rule).
- `generateMetadata` → SEO/content rules derived from data (`code` layer).

### Pages Router (`pages/`)
- `getServerSideProps` → data-fetch preconditions, redirect rules, auth gates (`code` layer).
- `getStaticProps` + `revalidate` → freshness/staleness rules (`config` layer).
- `getStaticPaths` + `fallback` → allowed-path enumeration rules (`batch` layer).

### Middleware (`middleware.ts`)
- Runs at edge before rendering → request-level gates (`code` layer).
- `NextResponse.redirect`, `.rewrite`, `.next()` with headers → routing rules (`code` layer).
- Matcher config (`config.matcher`) → scope of rule application (`config` layer).

### Server Actions
- `"use server"` functions → mutation rules living server-side (`code` layer).
- Input validation inside actions → authoritative business predicates (`code` or `rules_engine` layer).
- `revalidatePath`/`revalidateTag` calls → cache-invalidation rules (`workflow` layer).

### Route Handlers (`app/api/.../route.ts`)
- Exported `GET`, `POST`, etc. → HTTP-method-specific rules (`code` layer).
- Auth checks, body parsing, response shaping → service-layer constraints (`code` layer).

### Server-Client Boundary
- `"use client"` directive → marks client-only code; rules here are UI-enforced only (`ui` layer).
- Files without directive in `app/` → server components by default; rules are authoritative (`code` layer).
- Props passed across boundary → serialization constraints (no functions, classes, Dates) — structural, not typically a business rule.

### Cache & Freshness
- `fetch()` with `{ next: { revalidate: N } }` → time-based staleness rules (`config` layer).
- `{ cache: "no-store" }` → always-fresh requirement (`config` layer).
- `unstable_cache` / `revalidateTag` → tag-based invalidation rules (`workflow` layer).

## Dependency & Config Tracing

- Follow imports from UI component → hook → service → schema to find rule's authoritative source.
- Environment variables (`process.env.X`, `NEXT_PUBLIC_X`) → feature flags, thresholds, URLs (`config` layer).
- Config files (`constants.ts`, `config/`) → magic numbers, limits, toggles (`config` layer).
- Shared packages in monorepos → rules may live in `packages/shared/validators`.
- Re-exported barrel files (`index.ts`) may obscure rule origin — trace past them.

## Extraction Checklist

- [ ] Identify all runtime validation schemas and extract predicates (`rules_engine` layer).
- [ ] Map TypeScript types to candidate facts only — never promote without runtime evidence.
- [ ] Trace form validation → hook → service → schema chain; assign layers per mapping table.
- [ ] Catalog middleware rules (matchers, conditions, outcomes) as `code` layer evidence.
- [ ] Document server action preconditions and mutation guards.
- [ ] Identify `"use client"` boundary and classify rules by enforcement authority.
- [ ] For each duplicated client/server rule: compare subject, condition, threshold, outcome — merge if identical, conflict-link if different.
- [ ] Extract state machine transitions from reducers (`workflow` layer).
- [ ] Note cache/freshness rules and their business justification (`config` layer).
- [ ] Record config-driven thresholds, limits, and feature flags as parameterized rules.
- [ ] Check monorepo shared packages for cross-app rule definitions.
