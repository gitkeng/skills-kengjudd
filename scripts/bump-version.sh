#!/usr/bin/env bash
# Bump every repo-level version field in lockstep.
#
# Usage:
#   ./scripts/bump-version.sh <semver>      e.g. ./scripts/bump-version.sh 0.3.0
#   ./scripts/bump-version.sh --show        print the current values and exit
#
# There are FOUR repo-level version fields; they must always hold the same
# string, because Claude Code compares the marketplace plugin entry while
# scripts/update.sh and humans read VERSION:
#   1. VERSION
#   2. .claude-plugin/plugin.json           -> .version
#   3. .claude-plugin/marketplace.json      -> .metadata.version
#   4. .claude-plugin/marketplace.json      -> .plugins[0].version
#
# Per-skill versions (skills/<name>/SKILL.md metadata.version) are NOT touched —
# bump those by hand in the skill you changed.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

show() {
  echo "VERSION                                    $(cat VERSION)"
  python3 - <<'PY'
import json
p = json.load(open('.claude-plugin/plugin.json'))
m = json.load(open('.claude-plugin/marketplace.json'))
print(f"plugin.json .version                       {p['version']}")
print(f"marketplace.json .metadata.version         {m['metadata']['version']}")
print(f"marketplace.json .plugins[0].version       {m['plugins'][0]['version']}")
PY
}

if [[ $# -eq 0 ]]; then
  echo "Error: pass a SemVer string or --show. See --help." >&2
  exit 1
fi

case "$1" in
  -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  --show) show; exit 0 ;;
esac

NEW="$1"
if [[ ! "$NEW" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: '$NEW' is not a SemVer <major>.<minor>.<patch> string." >&2
  exit 1
fi

printf '%s\n' "$NEW" > VERSION
NEW="$NEW" python3 - <<'PY'
import json, os
new = os.environ['NEW']

with open('.claude-plugin/plugin.json') as f:
    plugin = json.load(f)
plugin['version'] = new
with open('.claude-plugin/plugin.json', 'w') as f:
    json.dump(plugin, f, indent=2)
    f.write('\n')

with open('.claude-plugin/marketplace.json') as f:
    market = json.load(f)
market['metadata']['version'] = new
for entry in market['plugins']:
    entry['version'] = new
with open('.claude-plugin/marketplace.json', 'w') as f:
    json.dump(market, f, indent=2)
    f.write('\n')
PY

echo "Bumped all four version fields to $NEW:"
show
echo ""
echo "Still to do by hand: CHANGELOG.md entry, and the changed skill's"
echo "metadata.version + metadata.updated in its SKILL.md."
