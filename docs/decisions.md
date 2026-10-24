# Decision log

Status: current (active decision log; ADR-012 §8). Every session skims this file, so keep it short.

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

- 2026-10-21 [workflow] Development is bottom-up, one domain at a time: DAQ first (rewrite from spec; legacy is reference only), then preprocess. Home: log-only.
- 2026-10-21 [repos] GitHub (`ufan`) is the default remote; legacy and support repositories may keep gitee or other remotes. Home: log-only.
