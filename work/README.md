# Work discovery and session scope

The [work index](index.yml) lists iterations for orientation. It may contain several active entries;
none is the global current iteration. `active` describes planning activity, not approval or readiness
of every task. The linked proposal and task documents own step, dependency and review details.
Paths in the index are relative to the workspace root. Update the index when an iteration starts,
pauses or completes, rather than updating `AGENTS.md`. Use statuses `active`, `paused`, `completed`.
Do not duplicate individual task status here. Register an iteration once its proposal/tasks exist;
ordinary maintenance and discussion do not need an iteration or index entry.

## Select the session scope

Use the user's current request or the supplied coordinator/batch assignment first. Read its relevant
instructions, specs and task context. An explicit assignment takes precedence over discovery; it
does not override safety rules, approval gates or task dependencies. A missing assigned record is
an error to report, not a reason to switch to another iteration.

Without an assignment, the index supplies context only. A human can discuss any topic without
selecting an iteration. An unattended session without a bounded assignment reports that it is
unassigned and stops; it must not take the first unchecked task or treat an active entry as a claim.

Session intent can change during conversation. Infer it from the request; do not require a mode
flag for ordinary human interaction.

| Intent | Expected behavior |
|---|---|
| Discussion, brainstorming, review | Read relevant context and answer. No mandatory edits, commits or iteration handoff. Record decisions when requested or when implementing an agreed change. |
| Directed implementation or maintenance | Complete the requested scope; run status before mutations, verify changed repositories and commit scoped changes. Update only the relevant task handoff, if one exists. |
| Backup or transfer | Follow the requested backup scope; inspect state as needed. Never interpret it as permission to push, delete, or advance an iteration. |
| Autonomous batch | Execute the explicitly assigned task or bounded task set, within its acceptance criteria, dependencies and stopping conditions. Report blockers instead of inventing approvals or expanding scope. |

## Lightweight assignment

A prompt or task document is sufficient; no new CLI, service or environment variables are required.
An autonomous assignment must identify:

- task identity and objective (for existing task tables, iteration ID plus row number is sufficient);
- allowed repositories/paths and input task/spec references;
- acceptance criteria and verification commands;
- working checkout/worktree and where results should be handed off;
- bounds: authorized task set, review gates, and what to do on blockers or failed verification.

For example: “Implement `daq-iteration-1/#4` in the assigned isolated core worktree. Use its task,
spec and review prerequisites; scope is the device FSM and its conformance tests. Run `muon verify
core`. Report the commit, verification and unresolved reviews to the coordinator; do not update the
shared iteration summary or proceed to #5.” This illustrates assignment shape, not readiness of #4.
For a human request, infer these details where clear rather than demanding a form.

## Parallel execution and handoff

The index and Markdown task tables provide no atomic claims, leases or scheduling. They are not
safe autonomous work queues. Concurrent writers use separate worktrees/checkouts and task branches;
use the same task branch name across repositories involved in that assignment. A user or coordinator
assigns non-overlapping scopes and integrates results. Do not commit another session's changes.

A worker reports its task ID, result, commit(s), verification, blockers and remaining approvals to its
assigned handoff destination. Only the designated integrator updates shared iteration summaries.
For human-directed iteration work, update that iteration's `## Next` with pending actions, questions
and hardware validation limits. Keep completed maintenance out of unrelated iteration handoffs.
Unrelated maintenance can be handed off through its commit and final report. Discussion requires no
repository handoff. Keep durable decisions in the decision log or ADRs.

Before adding autonomous claiming, scheduling or recovery infrastructure, evaluate the existing
[open-source candidates](../docs/notes/agent_coordination_options.md). This foundation implements
work discovery and scoped assignments; coordinated autonomous execution remains future work.
