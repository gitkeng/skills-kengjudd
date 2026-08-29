# Mainframe Playbook

Stack-specific extraction guidance for COBOL, JCL, PL/I, RPG, CICS, and related artifacts.

## Detection Signals

- File extensions: `.cbl`, `.cob`, `.cpy`, `.jcl`, `.proc`, `.pli`, `.pl1`, `.rpg`, `.rpgle`, `.bms`, `.mfs`
- JCL markers: `//` column-1 job cards, `EXEC PGM=`, `DD` statements
- COBOL divisions: `IDENTIFICATION DIVISION`, `DATA DIVISION`, `PROCEDURE DIVISION`
- Copybook inclusion: `COPY` statements in COBOL; `/COPY` in RPG
- CICS commands: `EXEC CICS` blocks
- File descriptors: `FD`, `SD`, `SELECT ... ASSIGN`

## Dependency Signals

- **Copybook usage:** `COPY member-name` traces shared data structures across programs. A copybook defining a record layout is a business entity definition.
- **JCL job flow:** `EXEC PGM=program` chains programs in sequence; `COND` parameters define conditional execution (business workflow). DD statements reveal file dependencies.
- **Called programs:** `CALL 'program-name'` and `EXEC CICS LINK/XCTL` reveal component interactions.
- **CICS transaction flow:** `TRANSID` definitions map to entry points; `COMMAREA` passes business context between programs.

## Mining Strategy

Prefer **bottom-up** for mainframe: start from outputs (reports, file writes, screen outputs) and trace back through the procedure division to identify the conditions that produce each business outcome.

### Definition-Use Tracing (Copybook/Config/JCL)

For every enforcement condition referencing a field, threshold, or constant:

1. **Resolve COPY inclusions:** follow `COPY member-name` to the copybook source. Gather the field's PIC clause, any 88-level condition names, and any VALUE clause establishing defaults or valid states as additional evidence entries.
2. **Trace to configuration:** if the enforced value matches or is loaded from a control parameter file, configuration table, or JCL SYSIN, add that definition site as evidence. The rule statement must incorporate the concrete value when the definition source supplies it.
3. **88-level condition names:** these define business-valid states (e.g., `88 STANDARD-OT-CAP VALUE 20.0`). When enforcement code tests the parent field, cite the 88-level definition as evidence alongside the procedure division check.
4. **JCL parameter inheritance:** PROC overrides and symbolic parameters (`SET`, `PARM=`) may supply runtime thresholds. Trace from the executing step to the parameter definition.

The goal: every rule enforcing a configurable threshold, valid-state list, or parameter-driven value must cite evidence from BOTH the enforcement site (procedure division) AND the definition site (copybook/config/JCL). Omitting the definition evidence is a completeness gap.

### Cross-Program Candidate Independence

When multiple programs enforce logic on the same business concept (e.g., both a calculation program and a validation program check the same field), register EACH enforcement as a separate candidate regardless of apparent redundancy. Programs in a batch pipeline execute at different stages — enforcement differences between them represent real business risk.

After per-file mining, compare candidates from different programs that address the same business topic (matching field names, same error condition semantics, overlapping glossary terms). Apply the merge/conflict policy: identical enforcement → merge; any difference in scope, threshold, exemption, or outcome → separate rules with bidirectional `conflicting_rule_ids`. Never pre-merge across program boundaries.

### Data Division as Entity Source

- `01`-level records in WORKING-STORAGE and FILE SECTION define business entities.
- `88`-level condition names ARE business rules — they define valid states: `88 VALID-STATUS VALUE 'A' 'S' 'P'`.
- `OCCURS` with `DEPENDING ON` reveals variable-length business structures.
- `REDEFINES` may indicate variant record types (multiple business entity subtypes in one physical record).

### Procedure Division Rule Patterns

- `IF`/`EVALUATE` statements with business-meaningful conditions (not just technical flags)
- `PERFORM` with `VARYING` and conditional exit = business iteration rules
- `COMPUTE`/`ADD`/`SUBTRACT`/`MULTIPLY`/`DIVIDE` with business-named variables = computation rules
- Paragraph/section names often encode business meaning: `2100-VALIDATE-CUSTOMER`, `3500-CALCULATE-PREMIUM`
- `INSPECT`/`STRING`/`UNSTRING` for format validation rules

### JCL as Workflow Source

- Job step sequencing = process workflow (extraction order, dependencies)
- `COND` parameters = conditional execution rules: `COND=(4,LT)` means "skip if prior RC < 4"
- `SORT` control statements in SYSIN = business ordering/aggregation logic
- GDG (Generation Data Group) patterns = versioning/retention policies
- Utility steps (IEBGENER, SORT, IDCAMS) with SYSIN control cards encode data transformation rules

### CICS Transaction Patterns

- `EXEC CICS RECEIVE MAP` → screen input handling (validation layer = `ui`)
- `EXEC CICS READ/WRITE/REWRITE` → data persistence rules
- `EXEC CICS SEND MAP` with attribute byte manipulation → conditional display logic
- `HANDLE CONDITION` → error/exception business policies

## PL/I Specifics

- `DECLARE` with `PICTURE` → data format constraints (like COBOL PIC)
- `ON` conditions → exception handling that may encode business rules
- `BEGIN...END` blocks with labels → logical business units
- `FETCH`/`CALL` → program-to-program dependencies

## RPG Specifics

- `/FREE` format (RPG IV): `IF`, `SELECT/WHEN`, `DOW/DOU` with business conditions
- Fixed-format indicators (`01`–`99`, `LR`, `OF`) encode state-based business logic
- File specifications with keys → entity relationships
- Calculation specs with result indicators → conditional business outcomes
- `BEGSR`/`ENDSR` subroutines → named business operations

## Encoding Considerations

- Source may have been transferred from EBCDIC (code pages 037, 500, 1047) to ASCII/UTF-8.
- Look for encoding artifacts: incorrect special characters, garbled comments.
- Note encoding issues in coverage; process readable content and flag undecodable sections.
- Column-sensitive formats (COBOL fixed-format columns 1–6, 7, 8–11, 12–72, 73–80) — respect column boundaries when extracting snippets.

## Evidence Layer Mapping

| Source Type | Layer |
|------------|-------|
| COBOL procedure division | `code` |
| COBOL 88-levels, data division constraints | `code` |
| JCL job steps and COND parameters | `batch` |
| SORT/utility control cards | `batch` |
| CICS screen maps and handlers | `ui` |
| Copybook record definitions | `code` |
| DB2 embedded SQL | `sql` |
| VSAM file definitions with keys | `db_constraint` |
| Control tables / parameter files | `config` |
