---
name: muon-domain-iteration
description: Use when starting or advancing a domain iteration (DAQ, preprocess, recon, ...). Drives the domain iteration playbook (engineering process §1), assigns autonomy classes (ship/show/ask), keeps the decision requests and tracks which step each capability is in.
---

# Domain iteration playbook

Engineering process §1. Steps are tracked **per capability** (§4 stages) in the iteration's
`proposal.md`. Exploration before a capability's baseline (prototypes, spikes) is allowed at any time
and does not advance its step.

## Autonomy classes

Every choice an agent makes in an iteration has an autonomy class (terms: engineering process §4).
Only `ask` waits for the owner.

| Class | Meaning | Record |
|---|---|---|
| `ship` | agent decides and proceeds | commit message |
| `show` | agent recommends and proceeds on it; an approver decides later | decision request in `proposal.md` `## Decision requests`, `Status: provisional` |
| `ask` | stop until the owner decides | decision request and `tasks.md` `blocked: owner` |

**Floor by path** (an agent may raise the class, never lower it):

- `ask`: hard stops (push; merge to `main`; archiving into `openspec/specs/`; importing into
  `testdata/golden`; strangler switch; retire); starting an iteration; any change to a requirement
  (`docs/requirements/`, a component requirement file), an ADR, `governance/` or the delegation policy;
  a breaking contract change; a change to a controlled capability's spec.
- `show`: a baseline change of a capability not yet controlled (`openspec/changes/`); additive changes in
  `core/contracts/`; `as-is.md` facts in dispute; golden fixture selection and tolerances; the domain
  boundary; a port/refactor/rewrite choice.
- `ship`: everything else (implementation behind an existing or provisional spec, tests, refactoring,
  docs that restate a decided fact).

**Escalation triggers** (engineering process §4, behaviour changes): if work turns out to change a
requirement, a controlled spec, a contract incompatibly, scientific interpretation beyond the
delegated envelope, or scope, stop and raise it as `ask`, whatever the step.

**Readiness is not approval.** A reviewer's "ready" report, passing tests or a missing objection never
approve anything. A provisional request is not a decision: nothing merges to `main` or is archived
while a request it depends on is still provisional.

## Checkpoints

| Step | Entry | Required evidence → exit | Class |
|---|---|---|---|
| 0 Scope | owner assignment starting the iteration | proposal and tasks from `iterations/_template/`; boundary and downstream needs in `docs/architecture/system_architecture.md` §5; proposed notes for the domain (skill `muon-promote`); entry in `work/index.yml` | start `ask`; boundary `show` |
| 1 Archaeology | step 0 recorded; legacy references locked | `as-is.md` (skill `muon-legacy-archaeology`): sources examined, observed vs assumed, citations; exit when every citation resolves and every discrepancy is a decision request or `blocked: external` | `show` |
| 2 Golden data | `as-is.md` draft | `golden-data.md`; fixtures with provenance; tolerances per quantity in machine-readable form (`tests/golden.yml`); exit when fixtures replay from T0 cuts or `testdata/scratch/` copies on the task branch (before import) | selection, tolerances `show`; import `ask` |
| 3 Baseline | `as-is.md` and golden plan exist (provisional is enough) | per capability, its first OpenSpec change (engineering process §4); provisional contracts; port/refactor/rewrite; promoted notes; exit when `openspec validate` passes, cited requirement IDs resolve, tasks cover the spec | change `show`; archive `ask` |
| 4 Skeleton | baseline change written | interfaces; failing contract and golden tests named after requirement IDs; exit when they fail for the stated reason | `ship` |
| 5 Implement | skeleton | code in isolated worktrees, one assignment per capability or feature; exit when `muon verify` passes and an independent review reports ready | `ship` |
| 6 Differential verify | implementation | automated comparison against golden data per quantity, as a report; exit when every quantity is within tolerance, or each deviation is classed `temporary` (scope and expiry, as a decision request) or `permanent` (an OpenSpec change) | within tolerance `ship`; deviation `ask` |
| 7 Strangler switch | step 6 exit; no provisional request left for the capability | new domain replaces legacy in the chain; contracts promoted; maturity in `.muon/repo.yml` | `ask` |
| 8 Retire | switch done | legacy tagged `legacy-final`, maturity `legacy`, inventory updated | `ask` |

Each step's open issues go to `tasks.md`, marked as blocking or not.
Statuses: `todo | draft | provisional | blocked: owner | blocked: external | done`. `blocked: owner`
means it needs the owner: an `ask` request (name its id) or an owner action such as hardware access.

## Decision requests and approval

- Each `show`/`ask` item is a decision request in `## Decision requests`: id, class, capability (or
  `all`), one question per request,
  recommendation, evidence (link), consequence if wrong, `Confirms when` (the evidence or event that
  makes it decidable, or `now`; approval follows it), status
  (`open` while no recommendation exists, then `provisional`, `approved` or `rejected`).
- The owner settles provisional requests in one pass, normally when work is about to merge.
  Approval record: `Status: approved — <approver>, human|agent:<tool/model>, <date>, authority: owner|delegation <id>`.
- `## Delegation` lists the classes of `show` requests the owner has granted to an agent approver,
  with conditions. The approver must be a different session from the author (engineering process §7).
  Hard stops, governance and the delegation policy itself are never delegated.
- At the end of an iteration, review the approved/rejected record and propose widening or narrowing
  the delegation.

## Backtracking

When a rejection or new evidence (e.g. a firmware answer) invalidates an earlier output, add an
entry to `## Revisions`: what changed, which downstream artifacts are affected, and which approvals
reopen (they return to `provisional`). Then redo the affected work.

## Roles and resuming

Roles are in engineering process §7. Workers make `ship` choices and propose `show` requests in their
handoff; only the integrator edits `## Decision requests`, `## Revisions`, task statuses and `## Next`. A
directed session without a named integrator is its own integrator.

To resume: use the explicit assignment first; otherwise discover iterations through
`platform/work/index.yml` (scope protocol in `platform/work/README.md`). Read the proposal and tasks to
establish each capability's step, the pending decision requests and the blockers. Continue only the authorized
scope (skill `muon-session`).
