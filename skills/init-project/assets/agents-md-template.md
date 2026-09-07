# AGENTS.md

<!-- init-project:start -->
## Project

- **Name:** <Project name>
- **Purpose:** <One or two sentences: what this project does and who it's for>
- **Stack:** <Primary language(s)/runtime, framework(s), package manager, test framework, lint/format tooling>

## Commands

<!-- The commands the user confirmed in the interview (coding/commands).
     Delete a line the project has no command for. -->
- `<install>` — install dependencies
- `<dev>` — run locally
- `<test>` — run the test suite
- `<lint>` — lint and format check
- `<build>` — production build

## Project knowledge base

- **Folder:** `<knowledge-base-folder>/` — an OKF (Open Knowledge Format)
  bundle. Start at `<knowledge-base-folder>/index.md` for the concept
  listing; `<knowledge-base-folder>/log.md` holds its change history and
  `<knowledge-base-folder>/kb-maintenance.md` the rules for adding to it.

## Working rules

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

<!-- karpathy:start -->
## Engineering guidelines (Karpathy)

Condensed from the [Karpathy guidelines](https://github.com/multica-ai/andrej-karpathy-skills) (MIT) — Andrej Karpathy's observations on LLM coding pitfalls, distilled into four principles:

1. **Think before coding.** Don't assume, don't hide confusion, surface tradeoffs — state assumptions explicitly, present alternatives instead of picking silently, and push back when a simpler approach exists.
2. **Simplicity first.** Minimum code that solves the problem, nothing speculative: no unrequested features, abstractions, or flexibility. If 200 lines could be 50, rewrite it.
3. **Surgical changes.** Touch only what you must; clean up only your own mess. Don't refactor or "improve" adjacent code — remove only the imports/variables your own change orphaned.
4. **Goal-driven execution.** Define verifiable success criteria and loop until met — e.g. "fix the bug" becomes "write a test that reproduces it, then make it pass."

Opt-out: delete this block, and answer "opt out" to the Karpathy question on the next init-project run — a re-run regenerates it while that answer is "include".
<!-- karpathy:end -->

## Agent notes

<!-- One bullet per agent selected during the interview, filled from the
     matrix extract. Each bullet is an imperative constraint for the
     agents that read this file later, not a note about the init run. For a
     native agent the bullet also names ONE quirk from the closed list: the
     file it reads, an init command that would overwrite this file (quote
     the command and its create-vs-update behavior from the matrix — "do not
     run <command> here"), or an import-expansion limit. For an adapter
     agent the quirk lives in that agent's own file. -->
- **<Agent name>:** <adapter kind (native / import-adapter / full-copy) and, for a native agent, the one quirk — e.g. "do not add @ imports — ZCode does not expand them"; "do not run /init here — it creates an AGENTS.md">
<!-- init-project:end -->
