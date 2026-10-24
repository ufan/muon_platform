---
name: muon-domain-iteration
description: Use when starting or advancing a domain iteration (DAQ, preprocess, recon, ...). Drives the ADR-010 playbook and tracks which step the domain is in.
---

# Domain iteration playbook

Steps (ADR-010 §4). Each step has an output; do not skip ahead without it.

| Step | Output | Who decides |
|---|---|---|
| 0 Scope | domain boundary and downstream needs in `platform/docs/architecture/architecture_overview.md` | user |
| 1 Archaeology | `as-is.md` (skill `muon-legacy-archaeology`) | agent drafts, user corrects |
| 2 Golden data | `golden-data.md`, fixtures in the project's `tests/` | agent |
| 3 To-be spec | spec deltas, provisional contracts, port / refactor / rewrite decision (prototype first is fine; a change proposal via `muon-new-change` when recording a baseline) | user approves |
| 4 Skeleton | interfaces and failing contract/golden tests | agent |
| 5 Implement | code | agents (separate worktrees) |
| 6 Differential verify | golden comparison passes; deviations documented in the spec | agent + user |
| 7 Strangler switch | new domain replaces legacy in the chain; contracts promoted; maturity updated in `.muon/repo.yml` | user |
| 8 Retire | legacy tagged `legacy-final`, maturity `legacy`, inventory updated | user |

To resume: use the explicit iteration/task assignment first; otherwise discover iterations through
`platform/work/index.yml` using the scope protocol in `platform/work/README.md`. Read the linked
proposal and tasks to establish the current step, dependencies and review gates. Continue only the
authorized scope. The integrator records the step in `proposal.md` and pending actions in `tasks.md`
`## Next`; parallel workers hand off their scoped results instead of editing that shared summary
(skill `muon-session`).
