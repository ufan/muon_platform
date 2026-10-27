# Decision log

Status: current (active decision log; [engineering process](engineering_process.md) §4). Every session skims this file, so keep it short.

## When to log

Log a decision only if all three hold:

1. The owner chose between real alternatives. Events and facts go in commit messages.
2. It constrains future work across sessions or repositories.
3. Its content or rationale is not fully captured by a document it changes.

Otherwise: a decision that changes a document is recorded by that edit and its commit message; a
consequential choice with alternatives becomes an ADR; an undecided question becomes an open point
in the owning document; an iteration item awaiting approval is a decision request in its iteration.

**Product or process.** This log belongs to the project process (`governance/`); it is never the
authority for the product. A product decision (requirements, architecture, interfaces, data formats,
scientific behaviour) may be logged when it is made, but must name its home in `docs/` or a component
repository, and lands there (engineering process §4). `log-only` is allowed only for process decisions.

## Format and lifecycle

One line, newest first: `YYYY-MM-DD [area] decision — why, when known. Home: <document> (pending) | <document> | log-only`.

- **Active:** listed below. `(pending)` marks a product decision its home does not state yet.
- **Folded:** once the home document states it, move the entry to [`decision_log/<year>.md`](decision_log/2026.md)
  with its home. Archived entries stay searchable for rationale.
- **Superseded:** replace the entry with the new one and archive the old one.

Fold entries at the end of each domain iteration, or when `muon doctor` warns (more than 30 active
entries). A product entry is never folded while its home is pending: land it first (skill `muon-promote`).

## Active decisions

- 2026-10-21 [workflow] Development is bottom-up, one domain at a time: DAQ first (rewrite from spec; legacy is reference only), then preprocess. Home: log-only.
- 2026-10-21 [repos] GitHub (`ufan`) is the default remote; legacy and support repositories may keep gitee or other remotes. Home: log-only.
