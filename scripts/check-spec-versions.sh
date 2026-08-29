#!/usr/bin/env bash
# Check whether the OKF spec version recorded in this repo's knowledge base is
# still the latest published version.
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
latest="$(printf '%s\n' "$spec_content" | grep -m1 -o 'Version [0-9]\+\.[0-9]\+' | sed 's/Version //')"
if [[ -z "$latest" ]]; then
  echo "Error: could not parse '**Version X.Y**' line from $SPEC_URL" >&2
  exit 2
fi

echo "Recorded OKF version (knowledge/specs/okf-spec.md): $recorded"
echo "Latest OKF version (canonical SPEC.md):             $latest"

if [[ "$recorded" == "$latest" ]]; then
  echo "OK: knowledge base matches the latest OKF spec."
  exit 0
fi

echo ""
echo "DRIFT: the OKF spec has changed. Before further KB work:"
echo "  1. Read the new spec: $SPEC_URL"
echo "  2. Update knowledge/specs/okf-spec.md (content + spec_version) and adjust"
echo "     the knowledge/ bundle to the new rules."
echo "  3. Record the migration in knowledge/log.md."
exit 1
