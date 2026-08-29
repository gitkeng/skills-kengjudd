# Data Layer Playbook

Stack-specific extraction guidance for SQL dialects, stored procedures, triggers, functions, and schema definitions.

## Detection Signals

- File extensions: `.sql`, `.ddl`, `.dml`, `.pks`, `.pkb`, `.prc`, `.fnc`, `.trg`, `.vw`
- Schema definition markers: `CREATE TABLE`, `CREATE INDEX`, `ALTER TABLE ADD CONSTRAINT`
- Procedural code: `CREATE PROCEDURE`, `CREATE FUNCTION`, `CREATE TRIGGER`, `CREATE PACKAGE`
- Migration files: numbered migrations (Flyway, Liquibase, EF, Alembic, ActiveRecord)
- Database-specific: `DELIMITER` (MySQL), `BEGIN...END` blocks, `DECLARE` sections

## Dependency Signals

- **Foreign key graphs:** `REFERENCES table(column)` defines entity relationships and ownership.
- **Stored procedure call graphs:** `EXEC proc_name` / `CALL proc_name` / package body calls reveal procedure dependencies.
- **View dependencies:** `SELECT ... FROM table/view` in view definitions reveal read dependencies.
- **Trigger targets:** `ON table_name` clauses link triggers to their controlling entities.
- **Cross-schema references:** `schema.table` prefixes reveal domain boundaries when schemas map to domains.

## Mining Strategy

Prefer **bottom-up** for data layers: start from constraints, triggers, and check expressions which explicitly encode business rules, then trace stored procedures that implement business operations.

### Schema Constraints as Rules

- `NOT NULL` → mandatory field (often plumbing, but business-significant when it encodes a policy like "every order must have a customer").
- `CHECK (expression)` → validation or data_integrity rule. Extract the full expression as evidence.
- `UNIQUE` / `UNIQUE INDEX` → uniqueness business rule (deduplicate with code-layer enforcement).
- `FOREIGN KEY ... ON DELETE CASCADE/SET NULL/RESTRICT` → referential integrity and lifecycle policy.
- `DEFAULT` values → may encode a business default (configurable initial state).
- Named constraints are evidence of intentional business rules; unnamed constraints require judgment.

### Triggers as Rules

- `BEFORE INSERT/UPDATE` triggers with validation checks → validation/constraint rules.
- `AFTER INSERT/UPDATE/DELETE` triggers that propagate changes → action_enabler rules.
- Triggers that maintain derived/computed columns → computation rules.
- Triggers that enforce cross-table consistency → data_integrity rules.
- Audit triggers (timestamp, user tracking) → typically plumbing unless audit itself is a business requirement.

### Stored Procedures and Functions

- Input parameter validation at procedure start → validation rules.
- Business conditionals (`IF`/`CASE`) controlling data modification → constraint/decision rules.
- Cursor-based processing with per-row business conditions → iteration-based rules.
- Transaction boundaries (`BEGIN TRANSACTION ... COMMIT/ROLLBACK`) hint at atomic business operations.
- Functions computing business values (tax, interest, scoring) → computation rules.
- Procedures called by application code vs. scheduled jobs — note the invocation context for layer classification.

### SQL Dialect Considerations

Syntax varies but business meaning is portable:

- **T-SQL:** `BEGIN...END`, `@@ROWCOUNT` checks, `TRY...CATCH` error handling, `MERGE` statements.
- **PL/SQL:** Package specs/bodies, `%TYPE`/`%ROWTYPE`, exception blocks with `RAISE_APPLICATION_ERROR`.
- **PL/pgSQL:** Dollar-quoted function bodies, `RAISE EXCEPTION`, `RETURNS TRIGGER`.
- **MySQL:** `DELIMITER` usage, limited CHECK constraint support (pre-8.0 — constraints may only exist in application code).
- **Db2:** SQL PL procedures, `SIGNAL SQLSTATE` for business exceptions, `IDENTITY` columns.

### Migration Files as Evidence

- Migration files are authoritative evidence of when constraints were added or modified.
- Use the latest migration state as current truth; note if constraints were removed (possible rule retirement).
- Migration comments often contain business justification — valuable context but never treat comments as authoritative over the actual DDL.

### Definition-Use Tracing

For stored procedures and functions that reference parameters, configuration tables, or constants defined elsewhere, trace backward to the definition site. Include the definition (lookup table row, function definition, declared constant) as evidence alongside the enforcement procedure. When a constraint references a function or sub-query, cite both the constraint and the referenced definition when the business value is only visible in the definition.

### Partitioning and Archival Rules

- Partition schemes (by date, by status, by tenant) may encode data lifecycle business rules.
- Scheduled purge/archive procedures → retention policy rules (process_workflow + data_integrity).

## Evidence Layer Mapping

| Source Type | Layer |
|------------|-------|
| Schema DDL (CREATE TABLE, constraints) | `db_constraint` |
| Triggers | `db_constraint` |
| Stored procedures and functions | `sql` |
| View definitions with business logic | `sql` |
| Migration files | `sql` or `db_constraint` (based on content) |
| Scheduled database jobs (DBMS_SCHEDULER, SQL Agent) | `batch` |
| Configuration tables / lookup data | `config` |
