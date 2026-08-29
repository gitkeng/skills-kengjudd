# Enterprise Legacy Playbook — ABAP & PowerBuilder

## Scope

Static, read-only extraction of business rules from SAP ABAP and Sybase/Appeon PowerBuilder codebases. No modifications to source systems. No chained references between sections.

---

## Detection, Inventory, and Evidence Layers

### ABAP inventory signals

Inventory reports, includes, classes/interfaces, function modules, table/view/domain definitions, selection screens, screen flow modules, background jobs, authorization checks, message/status definitions, configuration/value tables, variants, and enhancement/exit artifacts. Generated includes and transport/binary-only artifacts require explicit coverage treatment.

### PowerBuilder inventory signals

Inventory applications, libraries, windows, menus, visual and nonvisual user objects, DataWindows, event scripts, transaction objects, pipeline/timer processing, configuration reads, inheritance, and compiled-only external dependencies. Prefer readable source exports; never infer hidden logic from a compiled library.

### Canonical evidence layer mapping

| Artifact | `layer` value |
|---|---|
| Reports, includes, class/function methods, event scripts, NVO logic | `code` |
| Open/embedded query text, DataWindow SQL, stored-procedure calls | `sql` |
| Dictionary/domain checks, DataWindow required/value/update constraints | `db_constraint` |
| Background jobs, variants, periodic/timer processing | `batch` |
| Screen/event/status flow, transaction orchestration, enhancement flow | `workflow` |
| Selection-screen, window, menu, and DataWindow interaction validation | `ui` |
| Customizing/code tables, variants, INI/configuration values | `config` |
| Repository-local decision tables or declarative rule artifacts | `rules_engine` |

Generated and unavailable artifacts are coverage statuses, never `layer` values.

## 2 Unavailable Binary Handling

Unavailable or binary-only artifacts are coverage findings, not inferred rules.

- **Do not** fabricate logic from unavailable binaries.
- **Do not** guess rules from interface signatures alone.
- Log each as: artifact identifier, public interface metadata (if extractable), reason unavailable.
- PBD libraries: extract public method/event signatures from header metadata only.
- Kernel functions / missing includes: record opaque dependency with call site location.
- OCX/DLL: document interface contract (method names, parameters) without inferring behavior.

---

## 3 Merge / Conflict Policy

Compare copies across UI, application, database, enhancement, and batch tiers by subject scope, condition, threshold, and outcome.

- All four dimensions identical: merge into one rule and preserve all evidence locations.
- Any dimension differs: create separate rule records and set bidirectional `conflicting_rule_ids` between every contradictory pair.
- Add the discrepancy to each rule's `open_questions` and set `review.status` to `needs_review` when confidence is below high.
- Enhancement/exit code is an independent candidate; never assume it supersedes base behavior without activation evidence.
- Unavailable binaries cannot support rules or conflicts. Record absence as a coverage finding and do not infer hidden behavior.

## 4 Deduplication

- Unique key — ABAP: program name + include + line number. PowerBuilder: library + object + event + line number.
- Identical rules extracted from multiple passes: keep single entry, note all source locations.
- Enhancement/exit overlays: extract separately; do not merge into base artifact's rules.

---

## 5 Data Access Patterns

- **ABAP**: Open SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `MODIFY`), Native SQL, AMDP procedures, logical databases. Transaction boundaries via `COMMIT WORK`, `ROLLBACK WORK`, update-task function calls, `ENQUEUE`/`DEQUEUE` lock objects.
- **PowerBuilder**: DataWindow `Retrieve()`/`Update()`, embedded SQL, stored-procedure calls, transaction-object commit/rollback, DataWindow update properties (key columns, where-clause strategy).

---

## 6 Dependencies (Extraction Scope Only)

- **ABAP**: `INCLUDE`, `PERFORM … IN`, `CALL FUNCTION`, `CALL METHOD`, `SUBMIT`, `CALL TRANSACTION`, RFC destinations, BAdI `GET BADI`/`CALL BADI`, user exits.
- **PowerBuilder**: Ancestor inheritance, inter-window `OpenWith`/`OpenSheet`, cross-PBL function calls via library search order, dynamic library overrides, PFC hooks.

---

## 7 Selection & Validation Extraction

- **ABAP**: `PARAMETERS`/`SELECT-OPTIONS` declarations; `AT SELECTION-SCREEN ON <field>` validation blocks; `AT SELECTION-SCREEN OUTPUT` visibility control; variant values as implicit rules.
- **PowerBuilder**: `Validate` events, DataWindow column validation rules/expressions, `AcceptText()`/`ItemChanged`/`ItemError` scripts, `EditMask`/`Required`/`Values` properties, `ItemChanged` return codes (0=accept, 1=reject, 2=reject+focus).

---

## 8 Constants, Value Lists & Config-Driven Logic

- **ABAP**: `CONSTANTS`, domain fixed values, value tables, check tables, `TYPE-POOL` definitions, `TVARVC` reads feeding IF/CASE.
- **PowerBuilder**: Instance/shared variable constants, enumerated dropdown sources, code tables in DataWindow column specs, `ProfileString`/registry/DB-lookup feeding conditionals.

---

*Static extraction targets only. No source modification. No runtime dependency. No chained references.*
