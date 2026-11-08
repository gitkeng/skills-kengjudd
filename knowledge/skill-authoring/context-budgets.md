---
type: Playbook
title: Context budgets — what each agent loads from a skill and when
description: >
  The numbers that decide whether a skill's description is seen in full,
  whether its body survives compaction, and how many tokens the skill list
  costs every turn: Claude Code's 1,536-char description cap and 1% listing
  budget, its 5,000-token post-compaction re-attach limit, ZCode's 250-char
  excerpt, Kimi's 240-char fallback, Codex's description shortening, Zed's
  50 KB catalog — and the authoring rules that follow (first-240 trigger
  words, critical instructions in the first 5,000 tokens, one install
  channel per machine, short Updating sections).
tags:
  - agent-skills
  - context
  - tokens
  - descriptions
  - progressive-disclosure
  - claude-code
  - zcode
  - kimi-cli
  - codex
  - zed
sources:
  - resource: https://code.claude.com/docs/en/skills
    title: Claude Code docs — Skills (description + when_to_use truncated at 1,536 chars; listing budget 1% of context, skillListingBudgetFraction / SLASH_COMMAND_TOOL_CHAR_BUDGET; least-invoked descriptions dropped first; post-compaction re-attach of the first 5,000 tokens per skill within 25,000; skillOverrides on/name-only/user-invocable-only/off; hot reload and /reload-skills; /skill-doctor)
  - resource: https://agentskills.io/specification
    title: Agent Skills Specification (metadata ~100 tokens; body < 5,000 tokens recommended; under 500 lines)
  - resource: https://zcode.z.ai/en/docs/skill
    title: ZCode Skills docs (about 250 chars of description injected per turn; description over 1,024 chars drops the skill; body truncated at 100 KB)
  - resource: https://moonshotai.github.io/kimi-cli/en/customization/skills.html
    title: Kimi CLI Skills docs (description fallback truncated at 240 chars)
  - resource: https://learn.chatgpt.com/docs/build-skills.md
    title: Codex — Build skills (skills share 2% of context or 8,000 chars; Codex shortens descriptions first, then omits skills with a warning)
  - resource: https://zed.dev/docs/ai/skills
    title: Zed — Agent Skills (names and descriptions share a 50 KB catalog budget; description over 1,024 loads with a warning)
  - resource: https://ampcode.com/docs/customize/skills
    title: Amp — Skills (200 files per skill; discovery depth 5)
  - resource: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
    title: Anthropic — Skill authoring best practices ("the context window is a public good"; put the key use case first; TOC for references over 100 lines; Claude may head -100 nested files)
  - resource: https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop
    title: Anthropic Applied AI, 2026-10-22 — progressive disclosure of skills and tools cut Claude Code's system prompt by over 80%
  - resource: https://arxiv.org/html/2602.08004
    title: arXiv 2602.08004 (2026-02-08) — 40,285 public skills; SKILL.md median 1,414 tokens, 95th percentile 5,077, 99th 9,253
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-11-08T06:38:06Z"
status: stable
stale_after: "2027-02-08"
---

# Context budgets

Every number here was read on the cited page on 2026-11-08. Agents change
these limits without notice; re-check the sources when `stale_after` passes
or when a trigger test fails for no visible reason.

## Contents

1. What the skill list costs every turn
2. What each agent shows of a description
3. What survives inside a long task
4. Authoring rules that follow
5. Measuring instead of estimating

## 1. What the skill list costs every turn

| Agent | Listing budget | Over budget |
|---|---|---|
| Claude Code | 1% of the context window (setting `skillListingBudgetFraction`, env `SLASH_COMMAND_TOOL_CHAR_BUDGET`) | drops the **descriptions** of the least-invoked skills first; names always stay |
| Codex | 2% of context, or 8,000 chars when the window is unknown; `skills.max_context_tokens` up to 10,000 | shortens descriptions first, then omits skills with a warning |
| Zed | names + descriptions share a 50 KB catalog | — |
| spec (all agents) | ~100 tokens per skill for name + description | — |

Two consequences for this repo:

- **One install channel per machine.** A project symlink install
  (`.claude/skills/`) and the `kengjudd` plugin both active means every
  description is listed twice (~890 → ~1,800 tokens per turn for the seven
  skills in Nov 2026) and two identically named skills compete for the
  trigger. Pick one; `install.sh` warns when it sees the plugin installed.
- **Thai costs about 1 token per 1.5 characters**, roughly 2.7× English per
  character. Thai trigger phrases are worth it (they are what the user
  types) but keep them to the two or three a user actually says.

## 2. What each agent shows of a description

| Agent | Shown | Hard limit |
|---|---|---|
| Claude Code | up to 1,536 chars of `description` + `when_to_use` combined (`skillListingMaxDescChars`) | — |
| ZCode | about the first **250** chars per turn | > 1,024 chars → skill dropped |
| Kimi CLI | fallback truncated at **240** chars | — |
| Codex | shortened when over budget | — |
| Zed | full | > 1,024 → loads with a warning |
| spec | — | 1–1,024 chars |

Consequence: **the first 240 characters must carry the trigger on their
own** — what the skill does, when to use it, and the concrete words (including
Thai) a user types. Explanations of mechanism and "Not for …" exclusions come
after. Target 300–600 chars overall; Anthropic's guidance to "put the key use
case first" says the same thing from the other side.

## 3. What survives inside a long task

Claude Code does not re-read SKILL.md on later turns, and after context
compaction it re-attaches only the **first 5,000 tokens of each recently used
skill, within a combined 25,000-token budget**. A skill body longer than that
loses its tail exactly in the long runs where compaction happens.

Consequence: keep bodies under 5,000 tokens (the spec's number too), and put
rules that must hold for the whole task — iron rules, stop conditions, the
reference table — in the first screenfuls, never after the long workflow. Of
this repo's skills, only `init-project` exceeded the limit in Nov 2026
(≈6,350 tokens); release 0.16.0 moved Phase 1 and Phase 4 detail into two
references (≈4,926 tokens), 0.18.0 did the same for Phases 2–3 and tightened
the rest (≈4,094 tokens, 304 lines), and `doc2markdown` was split by document
type (≈4,320 → ≈2,311 tokens), with the eval suite confirming no behaviour
loss at each step.

Related loading facts worth knowing:

- Re-invoking an already-loaded identical skill adds a short "already loaded"
  note, not a second copy.
- Edited SKILL.md files hot-reload in Claude Code; a **new** skill directory
  needs `/reload-skills` or a new session. Zed live-reloads too.
- Subagents preload at most 32 skills (Claude Code 2.1.295).

## 4. Authoring rules that follow

1. Description: trigger complete in the first 240 chars; 300–600 chars total;
   third person; the Thai phrases users actually type.
2. Body: < 5,000 tokens; critical standing rules first; workflow detail that a
   phase needs only once goes to `references/` organised by variant so a run
   loads one file, not all of them.
3. Boilerplate that every activation pays for (this repo's `## Updating`)
   stays as short as the rule it satisfies allows — two commands and one
   sentence, not a tutorial.
4. Reference files over 100 lines start with a table of contents.
5. Never both channels on one machine.

## 5. Measuring instead of estimating

- `/skill-doctor` (Claude Code 2.1.261+) shows each skill's listing cost and
  how often it has been invoked; a skill that is never invoked on a machine is
  a candidate for `skillOverrides: name-only` in that user's settings — a
  user-side setting, so portability is untouched.
- `/context` shows the post-budget size of the Skills row.
- `claude plugin eval` reports tokens and duration per case with and without
  the skill ([/decisions/2026-11-08-eval-suite-layout.md](/decisions/2026-11-08-eval-suite-layout.md)).
- A character count ÷ 4 (English) or ÷ 1.5 (Thai) is good enough to rank
  skills by size; use the tools above before quoting a number.

## Related

- [/skill-authoring/best-practices.md](/skill-authoring/best-practices.md)
- [/specs/agent-skills-spec.md](/specs/agent-skills-spec.md)
- [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md)
