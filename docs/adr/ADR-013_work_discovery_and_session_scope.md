# ADR-013 Work discovery and session scope

Status: Accepted (2026-10-24; re-baselined 2026-10-25)

## Decision

- `AGENTS.md` stays stable and never names a current iteration. The work index (`work/index.yml`)
  lists iterations, possibly several active ones, and links to their records. It is for
  orientation, not a queue, lock or approval.
- An explicit user or coordinator assignment decides a session's scope. An unattended session
  without one stops.
- Session intent is inferred from the request: discussion needs no writes; directed changes are
  verified and committed in scope.
- Concurrent writers use separate worktrees; a designated integrator updates shared iteration
  summaries.
- Before building claims, leases or scheduling, evaluate existing tools
  ([options](../design/agent_coordination_options.md)).

## Why

Mixing project state into global rules, or routing all sessions through one iteration's task list,
misdirected work and could not allocate it safely.

## Consequences

Procedure: [work protocol](../../work/README.md) and skill `muon-session`. Safe unattended
competing workers are not solved here.
