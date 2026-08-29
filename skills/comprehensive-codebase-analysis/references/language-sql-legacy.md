# SQL and legacy-language playbook

## SQL

Detect dialect from connection providers, migration tools, syntax, and file conventions; never assume portability. Inventory DDL, constraints, indexes, views, routines, triggers, grants, dynamic SQL, seed data, and migrations. Map ORM operations to likely SQL and label inferred statements. Check missing keys/constraints, destructive migrations, non-idempotent scripts, injection construction, privilege breadth, transaction gaps, unbounded queries, cursor/loop hotspots, and dialect-specific behavior.

## COBOL and PL/I

Detect source dialect, compiler directives, fixed/free format, copybooks/include members, JCL or job-control integration, transaction monitors, database/file access, record layouts, and call conventions. Expand copybook relationships conceptually without executing preprocessors. Record program entry points, paragraphs/procedures, linkage sections, file status handling, numeric encodings, and external calls.

Treat copybooks and record layouts as shared interface/data contracts. Note dialect uncertainty, generated code, global state, fall-through control, unchecked status codes, batch restart/recovery, encoding, and date/precision assumptions. Use paragraph/statement evidence and label inferred call graphs where dynamic program names prevent verification.
