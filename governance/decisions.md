# Decision log

Status: current (active decision log; workflow/engineering_process.md §4). Every session skims this file, so keep it short.

## When to log

Log a decision only if all three hold:

1. The owner chose between real alternatives. Events and facts go in commit messages.
2. It constrains future work across sessions or repositories.
3. Its content or rationale is not fully captured by a document it changes.

Otherwise: a decision that changes a document is recorded by that edit and its commit message; a
consequential choice with alternatives becomes an ADR; an undecided question becomes an open point
in the owning document.

## Format and lifecycle

One line, newest first: `YYYY-MM-DD [area] decision — why, when known. Home: <document> | log-only`.

- **Active:** listed below.
- **Folded:** once the home document states it, move the entry to [`decisions/<year>.md`](decisions/2026.md)
  with its home. Archived entries stay searchable for rationale.
- **Superseded:** replace the entry with the new one and archive the old one.

Fold entries at the end of each domain iteration, or when `muon doctor` warns (more than 30 active entries).

## Active decisions

- 2026-10-26 [process] Adopt OpenSpec (pilot candidate E) for behaviour and contract changes only: a repo-local `openspec/` in each product repository (change and spec next to the code), plus platform as a small OpenSpec store for behaviour specs shared by domains (domain-service first; moves to `contracts` if it graduates), referenced read-only. Records: ADR = decision and rationale; iteration (`changes/`, to be renamed `iterations/`) = cross-repo plan and order; OpenSpec change = one approved behaviour change; OpenSpec spec = current behaviour; `FR-*` stay with their requirement files. Guardrails: muon schema with owner-only approval, pinned OpenSpec version, `muon` tool syncs the schema and store registration, specs merge only at archive, cross-repo `Depends on:` archived first. Rejected: drop (loses one approval gate across all AI tools and specs that stay current); all planning in a store (separates specs from code, beta, duplicates iterations). Revisit if stores are dropped or upgrades keep breaking the schema; fallback is repo-local only. Pilot changes were disposed unreviewed (owner) and are redone from scratch; evidence and log at tag `pilot/openspec-2026-10` (platform, core). Home: log-only until the redo writes engineering process §4.
- 2026-10-21 [workflow] Development is bottom-up, one domain at a time: DAQ first (rewrite from spec; legacy is reference only), then preprocess. Home: log-only.
- 2026-10-21 [repos] GitHub (`ufan`) is the default remote; legacy and support repositories may keep gitee or other remotes. Home: log-only.
