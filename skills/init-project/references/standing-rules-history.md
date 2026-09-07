# Standing-rules block history

Every version of the standing-rules block this skill has ever written,
verbatim, so that a re-run can tell **its own older block** from a block
the user edited. The block's single authoring home is still
`assets/agents-md-template.md` `## Working rules` — this file is a
deliberate, checked copy: `scripts/validate_output.py --self` fails when
the latest section here differs from the template by a single byte. Phase 4
**Baseline and block diff** compares the block found in an existing
`AGENTS.md` against these sections as a contiguous substring after
line-ending normalization only:

- matches the **latest** section → nothing to do;
- matches an **older** section → regenerate the current block verbatim and
  report "standing rules updated from <old> to <new>"
  (`report-format.md` section 3);
- matches **none** → the block was edited or translated: show the differing
  lines in the block diff for information, regenerate the current block
  verbatim (the block is never kept in an edited form), and report it.

Only this skill's maintainer adds a section, in the same change that edits
the template, with the skill version that ships it.

## Contents

- [1.1.0](#110)
- [1.0.0](#100)

## 1.1.0

Shipped by init-project 1.1.0 (2026-09-07). Bullets 2 and 3 keep their
opening text — `context-file-guidelines.md` `## Standing rules block`
anchors its override rules to "After finishing any piece of work" and
"When you learn something new about this project".

```markdown
- Start at this project's knowledge base index and open only the concepts
  the task needs; research externally only when the knowledge base does not
  already have the answer.
- After finishing any piece of work, update the knowledge base with what
  changed.
- When you learn something new about this project while working, capture it
  in the knowledge base — don't let it evaporate at the end of the session.
- When a knowledge source outside this repository has its own index (an OKF
  bundle, an LLMWiki, or similar), reference it by index + link and pull in
  only the excerpts you need — never copy it wholesale.
- Keep this file and its adapters current, but edit outside the
  `init-project` markers — a re-run regenerates what is inside them — and
  never let them bloat: once a detail stops being something you need on
  every turn, move it into the knowledge base and link it from here instead.
- Before changing the knowledge base, follow the `kb-maintenance.md` file in
  this project's knowledge base: it carries the format contract and the OKF
  spec-version check — never migrate silently and never ignore the drift.
```

## 1.0.0

Shipped by init-project 1.0.0 (2026-08-31).

```markdown
- Read this project's knowledge base first, and research externally only
  when the knowledge base does not already have the answer.
- After finishing any piece of work, update the knowledge base with what
  changed.
- When you learn something new about this project while working, capture it
  in the knowledge base — don't let it evaporate at the end of the session.
- When a knowledge source outside this repository has its own index (an OKF
  bundle, an LLMWiki, or similar), reference it by index + link and pull in
  only the excerpts you need — never copy it wholesale.
- Keep this file and its adapters current every work cycle, but never let
  them bloat: once a detail stops being something you need on every turn,
  move it into the knowledge base and link it from here instead.
- Watch the OKF spec version: when you have web access, fetch
  `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md`
  and read its `**Version X.Y**` line before knowledge-base work. When that
  version is newer than the `okf_version` recorded in the knowledge base's
  index, propose a migration to the user — never migrate silently and never
  ignore the drift. With no web access, work against the recorded
  `okf_version` and say that the check was skipped.
```
