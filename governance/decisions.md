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

- 2026-10-26 [process] Adopt OpenSpec inside component repositories only, for behaviour specs and their changes; no platform store. A capability is under change control from its first approved spec in `openspec/specs/` (before that it is in exploration: prototypes, no gate). Configuration is `openspec/config.yaml` rules and apply/archive guidance (owner-only approval, `FR-*` citations, verification tasks) from a platform template, with no forked OpenSpec workflow. Platform stays the system level (SRD, system architecture, ADRs, governance) plus iterations (`changes/`, to be renamed `iterations/`), which plan and order cross-repository work and link the component changes; `muon-new-change` is retired in the redo. Component repositories mirror the same process internally: requirements flow down from platform, and only contracts and published specs are visible outside. Shared system behaviour (domain-service) is specified where its contract lives: core now, `contracts` after extraction. Why: the pilot's gains (one approval gate across AI tools, specs merged at archive, testable scenarios) are all repository-local; a store adds little in one workspace and splits a contract from its consumer (§4). Revisit a store at the hardening trigger in §5. Pilot changes disposed unreviewed (owner), redone from scratch; evidence at tag `pilot/openspec-2026-10` (platform, core). Home: log-only until the redo writes engineering process §2 (system and component levels) and §4 (exploration, baseline, controlled stages).
- 2026-10-21 [workflow] Development is bottom-up, one domain at a time: DAQ first (rewrite from spec; legacy is reference only), then preprocess. Home: log-only.
- 2026-10-21 [repos] GitHub (`ufan`) is the default remote; legacy and support repositories may keep gitee or other remotes. Home: log-only.
