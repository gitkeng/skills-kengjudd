# business-rules-extraction

Statically extracts, documents, and verifies business rules from any codebase. Produces
domain-decomposed rule catalogs with line-level evidence, acceptance criteria, and
mechanical validation.

Version: 1.0.1 (skills-kengjudd numbering; imported from `gitkeng/aws-kiro-atx-lab`
where it was numbered 1.1.0 — see `metadata.upstream` in `SKILL.md`)  
License: MIT

## Dedicated Language Playbooks

The general workflow applies to any language. Dedicated stack guidance is bundled for:

- Mainframe: COBOL/JCL, PL/I, RPG, and CICS artifacts
- JVM and .NET: Java/Kotlin and C#/VB.NET
- Scripting/data: Python, Ruby, PHP, JavaScript, TypeScript, and SQL/data-layer artifacts
- Systems and UI: Go, Rust, Dart/Flutter, TypeScript/React/Next.js, C/C++, and Swift/Objective-C
- Concurrent and automation: Erlang/Elixir and Bash/PowerShell
- Enterprise legacy: ABAP and PowerBuilder

Each playbook supplies stack-specific detection, dependency signals, definition-use tracing,
rule-versus-plumbing guidance, evidence-layer mapping, and merge/conflict checks. Unlisted
languages use the language-agnostic procedure in `SKILL.md`.

## Installation

This skill follows the [Agent Skills](https://agentskills.io) open standard and
is distributed from the `skills-kengjudd` repository. Install it with the repo's
installer rather than copying the directory by hand — run from the repo root:

```bash
./scripts/install.sh --tool claude                        # user scope
./scripts/install.sh --tool claude --project /path/to/prj # project scope
```

`--tool` accepts `claude|codex|cursor|opencode|gemini|zed|goose|kimi|amp|kiro|zcode|all`.
Claude Code users can instead install the whole collection as a plugin
(`/plugin install kengjudd@kengjudd`). Update commands for both channels
are in `SKILL.md` § Updating.

## Usage

Trigger the skill by asking your agent to:
- "Extract business rules from this codebase"
- "Document the business logic"
- "Reverse engineer requirements from this system"
- "What does this system do?"
- "Analyze this legacy system"

The skill guides the agent through a two-pass extraction methodology and produces
a validated output tree with machine-readable rule catalogs, human documentation,
and SME review artifacts.

## Validator

After extraction, validate the output mechanically:

```bash
python3 scripts/validate_output.py <output-dir> --repo <analyzed-repo-root>
```

Options:
- `--repo <path>` — enables evidence verification (path existence, line range, snippet containment) and coverage completeness checks
- `--format text|json` — output format (default: text)

Exit codes:
- `0` — all checks passed
- `1` — one or more validation failures
- `2` — usage or IO error

Interpreter fallback: if `python3` is not available, try `python` or `py -3`.

### CI Integration

```yaml
# Generic CI step — adjust SKILL_PATH to your tool's skill location
# e.g., skills/business-rules-extraction in a skills-kengjudd checkout,
#       ~/.claude/skills/business-rules-extraction after install.sh --tool claude
- name: Validate extraction output
  env:
    SKILL_PATH: skills/business-rules-extraction
  run: python3 $SKILL_PATH/scripts/validate_output.py ./business-rules-output --repo . --format json
```

The validator uses only Python standard library modules — no additional dependencies required. Requires Python 3.8+.

## Output Structure

See `references/output-templates.md` for complete templates. Summary:

```
business-rules-output/
├── 00-index.md, manifest.json, coverage.json, glossary.md
├── domains/<slug>/rules.json    # canonical machine-readable catalog
├── domains/<slug>/*.md          # human documentation
├── cross-cutting/               # shared concerns
├── database/                    # schema reconstruction
└── exports/                     # optional CSV, Gherkin, DMN
```

## Validation Check Classes

1. Schema validation (manifest + all rules.json)
2. Entity ownership (no orphans, no undeclared sharing)
3. Rule ID format and global uniqueness
4. Rule shape (required fields, enums, evidence nonempty, category↔type consistency)
5. Rule cross-links resolve; conflicts bidirectional
6. Business-context anchors present
7. Coverage completeness and totals reconciliation
8. Evidence file existence, line range validity, snippet containment
9. Manifest↔rules.json rule count agreement
10. No empty/stub files in required output tree
