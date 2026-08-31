# AGENTS.md

## Project

- **Name:** <Project name>
- **Purpose:** <One or two sentences: what this project does and who it's for>
- **Stack:** <Primary language(s)/runtime, framework(s), package manager, test framework, lint/format tooling>

## Knowledge base

- **Folder:** `<knowledge-base-folder>/` — an OKF (Open Knowledge Format)
  bundle. Start at `<knowledge-base-folder>/index.md` for the concept
  listing; `<knowledge-base-folder>/log.md` holds its change history.
- **Read-first rule:** see `## Working rules` below — read the knowledge
  base before researching externally, and keep it updated as you work.

## Working rules

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
- Watch the OKF spec version: fetch
  `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md`
  and read its `**Version X.Y**` line before knowledge-base work. When that
  version is newer than the `okf_version` recorded in the knowledge base's
  index, propose a migration to the user — never migrate silently and never
  ignore the drift.

<!-- karpathy:start -->
## Engineering guidelines (Karpathy)

Condensed from the [Karpathy guidelines](https://github.com/multica-ai/andrej-karpathy-skills) (MIT) — Andrej Karpathy's observations on LLM coding pitfalls, distilled into four principles:

1. **Think before coding.** Don't assume, don't hide confusion, surface tradeoffs — state assumptions explicitly, present alternatives instead of picking silently, and push back when a simpler approach exists.
2. **Simplicity first.** Minimum code that solves the problem, nothing speculative: no unrequested features, abstractions, or flexibility. If 200 lines could be 50, rewrite it.
3. **Surgical changes.** Touch only what you must; clean up only your own mess. Don't refactor or "improve" adjacent code — remove only the imports/variables your own change orphaned.
4. **Goal-driven execution.** Define verifiable success criteria and loop until met — e.g. "fix the bug" becomes "write a test that reproduces it, then make it pass."

Opt-out: delete this block.
<!-- karpathy:end -->

## Agent notes

<!-- One bullet per agent selected during the interview, filled from
     references/agent-context-matrix.md. -->
- **<Agent name>:** <adapter kind (native / import-adapter / full-copy) and the one quirk worth surfacing — e.g. "reads CLAUDE.md, never AGENTS.md">
