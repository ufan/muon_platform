---
name: muon-domain-iteration
description: Use when starting or advancing a domain iteration (DAQ, preprocess, recon, ...). Drives the ADR-010 playbook and tracks which step the domain is in.
---

# Domain iteration playbook

Steps (ADR-010 §4). Each step has an output; do not skip ahead without it.

| Step | Output | Who decides |
|---|---|---|
| 0 Scope | domain boundary and downstream needs in `platform/docs/architecture/LANDSCAPE.md` | user |
| 1 Archaeology | `as-is.md` (skill `muon-legacy-archaeology`) | agent drafts, user corrects |
| 2 Golden data | `golden-data.md`, fixtures in the project's `tests/` | agent |
| 3 To-be spec | change proposal (skill `muon-new-change`): spec deltas, provisional contracts, port / refactor / rewrite decision | user approves |
| 4 Skeleton | interfaces and failing contract/golden tests | agent |
| 5 Implement | code | agents (separate worktrees) |
| 6 Differential verify | golden comparison passes; deviations documented in the spec | agent + user |
| 7 Strangler switch | new domain replaces legacy in the chain; contracts promoted; `west.yml` maturity updated | user |
| 8 Retire | legacy tagged `legacy-final`, maturity `legacy`, inventory updated | user |

To resume: read the domain's change directory in `platform/changes/`, find the last completed step, and continue from there. Keep the current step recorded in `proposal.md`.
