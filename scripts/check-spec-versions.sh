#!/usr/bin/env bash
# Check whether the spec versions recorded in this repo's knowledge base are
# still the latest published ones:
#   1. OKF  — knowledge/specs/okf-spec.md   spec_version   vs the canonical SPEC.md
#   2. Agent Skills — knowledge/specs/agent-skills-spec.md spec_source_commit
#      vs the last commit touching docs/specification.mdx in agentskills/agentskills
#      (the spec publishes no version number; the commit is the only marker).
#
# Canonical OKF spec: https://github.com/GoogleCloudPlatform/open-knowledge-format
# (the copy under GoogleCloudPlatform/knowledge-catalog/okf/ is a frozen,
# unmaintained snapshot — do not use it).
#
# The spec declares its version in a '**Version X.Y**' line near the top of
# SPEC.md; the repo has no git tags or releases, so that line is the only
# version source.
#
# Exit codes: 0 = up to date, 1 = drift detected (KB needs updating), 2 = error.
# Both checks always run; the exit code is the worst of the two.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB_FILE="$REPO_ROOT/knowledge/specs/okf-spec.md"
SPEC_URL="https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md"

if [[ ! -f "$KB_FILE" ]]; then
  echo "Error: $KB_FILE not found." >&2
  exit 2
fi

recorded="$(grep -m1 '^spec_version:' "$KB_FILE" | sed 's/spec_version:[[:space:]]*"\{0,1\}//; s/"\{0,1\}[[:space:]]*$//')"
if [[ -z "$recorded" ]]; then
  echo "Error: no 'spec_version:' key found in $KB_FILE frontmatter." >&2
  exit 2
fi

# Buffer the whole file first: piping curl straight into 'grep -m1' closes the
# pipe early and trips pipefail with curl exit 56.
spec_content="$(curl -fsSL "$SPEC_URL")"
# Anchor to the '**Version X.Y**' declaration line. A loose match anywhere in
# the document could pick up a "Changes since Version 0.2" reference and report
# a stale version as current — a silent false negative on the exact event this
# check exists to catch.
latest="$(printf '%s\n' "$spec_content" | grep -m1 -oE '^\*\*Version [0-9]+\.[0-9]+(\.[0-9]+)?\*\*' | sed 's/\*\*Version //; s/\*\*//')"
if [[ -z "$latest" ]]; then
  echo "Error: no '**Version X.Y**' declaration line found in $SPEC_URL." >&2
  echo "The spec's format may have changed — read it manually before trusting the KB." >&2
  exit 2
fi

echo "Recorded OKF version (knowledge/specs/okf-spec.md): $recorded"
echo "Latest OKF version (canonical SPEC.md):             $latest"

status=0
if [[ "$recorded" == "$latest" ]]; then
  echo "OK: knowledge base matches the latest OKF spec."
else
  echo ""
  echo "DRIFT: the OKF spec has changed. Before further KB work:"
  echo "  1. Read the new spec: $SPEC_URL"
  echo "  2. Update knowledge/specs/okf-spec.md (content + spec_version) and adjust"
  echo "     the knowledge/ bundle to the new rules."
  echo "  3. Record the migration in knowledge/log.md."
  status=1
fi

# ---------------------------------------------------------------------------
# 2. Agent Skills specification (agentskills.io)
# ---------------------------------------------------------------------------
AS_FILE="$REPO_ROOT/knowledge/specs/agent-skills-spec.md"
AS_PATH="$(grep -m1 '^spec_source_path:' "$AS_FILE" | sed 's/spec_source_path:[[:space:]]*"\{0,1\}//; s/"\{0,1\}[[:space:]]*$//')"
AS_RECORDED="$(grep -m1 '^spec_source_commit:' "$AS_FILE" | sed 's/spec_source_commit:[[:space:]]*"\{0,1\}//; s/"\{0,1\}[[:space:]]*$//')"
if [[ -z "$AS_PATH" || -z "$AS_RECORDED" ]]; then
  echo "Error: spec_source_path / spec_source_commit missing in $AS_FILE frontmatter." >&2
  exit 2
fi
AS_API="https://api.github.com/repos/agentskills/agentskills/commits?path=${AS_PATH}&per_page=1"
as_json="$(curl -fsSL -H 'Accept: application/vnd.github+json' "$AS_API")"
as_latest="$(printf '%s' "$as_json" | grep -m1 -oE '"sha": *"[0-9a-f]{40}"' | grep -oE '[0-9a-f]{40}' || true)"
as_date="$(printf '%s' "$as_json" | grep -m1 -oE '"date": *"[0-9T:Z-]+"' | grep -oE '[0-9T:Z-]{20}' || true)"
if [[ -z "$as_latest" ]]; then
  echo "Error: could not read the latest commit for $AS_PATH from the GitHub API." >&2
  echo "Rate-limited or offline? Try again later; do not assume the spec is unchanged." >&2
  exit 2
fi
echo ""
echo "Recorded Agent Skills spec commit (knowledge/specs/agent-skills-spec.md): $AS_RECORDED"
echo "Latest commit touching $AS_PATH:                 ${as_latest:0:12} ($as_date)"
if [[ "$as_latest" == "$AS_RECORDED"* ]]; then
  echo "OK: knowledge base matches the latest Agent Skills spec page."
else
  echo ""
  echo "DRIFT: the Agent Skills spec page has changed since the recorded commit. Before further KB work:"
  echo "  1. Read the diff: https://github.com/agentskills/agentskills/compare/${AS_RECORDED}...${as_latest:0:12}"
  echo "  2. Update knowledge/specs/agent-skills-spec.md (content + spec_source_commit)"
  echo "     and re-check skills/ against any changed rule."
  echo "  3. Record the migration in knowledge/log.md."
  status=1
fi

exit "$status"
