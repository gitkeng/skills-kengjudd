# Eval suite

Cases for `claude plugin eval` (Claude Code 2.1.269+), one directory per
skill and scenario. Layout, grader conventions and the synthetic-fixture rule:
`knowledge/decisions/2026-11-08-eval-suite-layout.md`. This directory is a
repo convention — it is not part of any skill and is not listed in
`.claude-plugin/plugin.json`.

| Case | Checks |
|---|---|
| `git-commit-thai-commit` | skill fires on "คอมมิตให้หน่อย"; proposes emoji+type subjects; splits concerns; **never** runs `git commit` without approval |
| `git-commit-ignores-git-question` | a git *question* does not trigger the skill |
| `doc2markdown-thai-docx` | skill fires on a Thai convert request; runs the bundled extractor; `brief.md` keeps the table |
| `doc2markdown-ignores-authoring` | writing a new Markdown document does not trigger the skill |

Fixtures are synthetic and live inside each case (`scaffold.sh`, optional
`fixtures/`). Never add a real document or repository.

Run from the repo root. Scaffold scripts and non-read-only tools run only with
the flags below. Grant `Bash` whole: every command runs inside Claude Code's
OS sandbox (writes confined to the run workspace, no network except the
domains granted), and a pattern grant such as `Bash(git *)` fails as soon as
the skill chains two commands with `&&`. The `WebFetch(domain:…)` grants let
`uv` fetch the extractor's inline dependencies on first run.

```bash
claude plugin eval . --scaffold --trust-plugin --no-publish \
  --allow-tools Bash Write Edit \
  "WebFetch(domain:pypi.org)" "WebFetch(domain:files.pythonhosted.org)" \
  --threshold 0.8 -j 4
```

Known sandbox quirk: Apple's `/usr/bin/git` shim fails inside the sandbox
(it cannot write its xcrun cache); runs fall back to Homebrew git on their
own, so keep a non-shim `git` on `PATH`.

Add `--case '<glob>'` to run a subset (one glob, e.g. `'git-commit-*'`),
`--runs 1` for a quick smoke run, `--max-cost-usd <n>` for a budget, and
`--keep-temp` to keep each run's sandbox and trace for inspection. Results land in
`evals/results/<timestamp>/` (`report.html`, `aggregate-result.json`), which
is git-ignored. Graders of type `tool_used: Skill` are plugin-fired indicators
in a two-arm run; the `min: 0 / max: 0 / arm: both` form is the anti-trigger
assertion.
