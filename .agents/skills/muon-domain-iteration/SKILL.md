---
name: muon-domain-iteration
description: Use when starting or advancing a domain iteration (DAQ, preprocess, recon, ...). Drives the domain iteration playbook (engineering process §1) and tracks which step the domain is in.
---

# Domain iteration playbook

Steps (engineering process §1). Each step has an output; do not skip ahead without it.

| Step | Output | Who decides |
|---|---|---|
| 0 Scope | domain boundary and downstream needs in `platform/docs/architecture/architecture_overview.md`; list the proposed design notes that touch the domain (skill `muon-promote`, step 1) | user |
| 1 Archaeology | `as-is.md` (skill `muon-legacy-archaeology`) | agent drafts, user corrects |
| 2 Golden data | `golden-data.md`, fixtures in the project's `tests/` | agent |
| 3 To-be spec (baseline) | for each capability: the first OpenSpec change in its component repository, creating its spec from what exploration and archaeology taught (engineering process §4); provisional contracts; port / refactor / rewrite decision; content from the listed design notes promoted with skill `muon-promote` | user approves each change |
| 4 Skeleton | interfaces and failing contract/golden tests | agent |
| 5 Implement | code, through approved OpenSpec changes once a capability is baselined | agents (separate worktrees) |
| 6 Differential verify | golden comparison passes; deviations documented in the spec (an OpenSpec change if behaviour is decided) | agent + user |
| 7 Strangler switch | new domain replaces legacy in the chain; contracts promoted; maturity updated in `.muon/repo.yml` | user |
| 8 Retire | legacy tagged `legacy-final`, maturity `legacy`, inventory updated | user |

To resume: use the explicit iteration/task assignment first; otherwise discover iterations through
`platform/work/index.yml` using the scope protocol in `platform/work/README.md`. Read the linked
proposal and tasks to establish the current step, dependencies and review gates. Continue only the
authorized scope. The integrator records the step in `proposal.md` and pending actions in `tasks.md`
`## Next`; parallel workers hand off their scoped results instead of editing that shared summary
(skill `muon-session`).
