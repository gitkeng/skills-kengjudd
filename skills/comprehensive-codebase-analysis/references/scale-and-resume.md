# Scale and resume

## Inventory first

Exclude generated output, dependency caches, binaries, vendored/minified assets, and generated code from deep reading, but record exclusions and reasons. Count files and lines with existing `cloc` when available; otherwise count readable source lines and label the result estimated.

## Depth selection

For a small repository, fully read all first-party source and configuration. For a large repository:

1. Rank components by source size.
2. Add optional version-control churn when `git` is available; do not require it.
3. Estimate centrality from imports, references, routes, build relationships, and data ownership.
4. Fully read the highest combined-risk components and security boundaries.
5. Sample the remainder across languages, layers, and entry points.
6. Record each component as `fully-read`, `sampled`, or `inventory-only`, including sampled files and rationale.

A user focus changes depth, not required output: analyze the focus fully, inventory everything else, and still produce the executive summary.

## Checkpoints

After each phase, atomically replace `progress.json` by writing valid complete JSON. Record phase status, timestamps, completed artifacts, coverage, and the next phase. On interruption set status `interrupted` when possible.

On resume, verify repository root, output root, schema version, and completed artifact presence. Continue after the last completed phase. Do not redo complete phases unless their files are missing or invalid. Preserve the prior manifest snapshot until final synthesis.

## Graceful degradation

- No `git`: omit churn/history and state the limitation.
- No `cloc`: use deterministic file/line counts and label estimates.
- No network: retain file-evidenced versions and add verification pointers; do not claim current latest/EOL facts.
- Unreadable/binary files: inventory by path and label not inspected.
