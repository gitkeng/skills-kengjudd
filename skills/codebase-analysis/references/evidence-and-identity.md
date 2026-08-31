# Evidence, identity, and re-runs

## Evidence

Use repo-relative forward-slash paths. A verified claim cites `path:line` or `path:start-end`; cite a path only for facts inherently represented by a whole file or directory. Quote the smallest useful excerpt. Label each claim `verified`, `inferred`, or `assumption`. Explain the evidence chain for inferred claims. Never manufacture line numbers.

A finding is a concrete located defect or risk, not generic advice. Record it once in `manifest.json` and cross-link prose to its alias.

## Canonical keys

Construct a canonical key as:

`<registry>:<normalized-file-path>:<finding-kind>:<discriminator>`

- Registry is `br`, `td`, `v`, `tc`, or `cmp`. Register non-security defects as `td` and vulnerabilities as `v`.
- Normalize the repo-relative path to lowercase where the repository is case-insensitive, retain forward slashes, remove `./`, and percent-encode literal `:` characters.
- Make `finding-kind` a stable lowercase hyphen slug describing the defect or rule, not its prose title.
- Use the containing member or symbol slug as discriminator. If no symbol exists, use the ordinal of first occurrence within that file for the same kind, ordered by source location.
- Never use traversal order, severity, mutable wording, or alias number in a canonical key.
- For components, use the defining directory/file plus a namespace/module slug.

Examples use generic paths: `v:src/auth/handler.cs:missing-request-token:submit`, `br:src/orders/service.py:minimum-total:place-order`, `cmp:src/billing:component:billing`.

## Human aliases

Use `BR-NNN`, `TD-NNN`, `V-NNN`, `TC-NNN`, and `CMP-NNN`. Load the prior manifest, match canonical keys first, and preserve matched aliases. Mint each next alias from the greatest prior/current number in that registry. Never renumber gaps.

## Manifest records

Each finding stores canonical key, alias, registry, title, kind, severity, confidence, status, and nonempty evidence. Components store canonical key, `CMP-NNN`, path, and optional namespace. Test cases store canonical key, `TC-NNN`, category, title, and source aliases. `traceability` stores explicit BR-to-TC links.

## Delta

Compare only canonical-key membership and severity:

- `new`: current key absent previously.
- `resolved`: prior key absent currently.
- `regressed`: present in both with higher current severity.
- `persisted`: present in both and not regressed.

Do not infer change from title, description, line movement, or prose. Keep resolved prior entries in `delta.resolved`, not in current findings. Mark a remediation action resolved only when all linked findings are resolved.
