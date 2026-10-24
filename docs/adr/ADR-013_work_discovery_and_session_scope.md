# ADR-013 Work Discovery and Session Scope

Status: Accepted (2026-10-24; owner agreement in discussion)
Supersedes: [ADR-012](ADR-012_repository_baseline_and_workflow.md) §8 global active-iteration discovery and universal iteration handoff rules only
Related: [ADR-010](ADR-010_spec_driven_domain_iteration.md) (domain playbook)

## Context

A changing iteration pointer in global agent instructions mixes stable rules with project state.
A universal `tasks.md` handoff also directs discussion and unrelated maintenance into one iteration.
Independent workers need explicit scope; discovering an active plan cannot safely allocate work.
Human discussions, backups and directed changes must coexist with assigned autonomous batches.

## Decision

- Keep `AGENTS.md` stable: it points to `work/index.yml` and the session protocol, not a current iteration.
- The versioned work index allows multiple active iterations and links to their proposal/task records.
  It is a discovery document, not a scheduler, lock or approval. Linked records own detailed plan state.
- The explicit user/coordinator assignment takes precedence over discovery, within existing rules,
  dependencies and approval gates. Unassigned unattended sessions stop without taking work.
- Infer session intent from the request. Discussion needs no repository writes; directed changes
  use normal verification and scoped commits. Backup requests retain their explicit scope.
- Concurrent writers use isolated worktrees/checkouts. Workers hand off scoped results; the
  designated integrator maintains shared iteration summaries. No global ownership service is added.
- Evaluate existing open-source coordination tools before implementing claims, leases or scheduling.

Detailed procedure: [work discovery and session scope](../../work/README.md), implemented through
[muon-session](../../.agents/skills/muon-session/SKILL.md). Candidate research:
[agent coordination options](../guide/agent-coordination-options.md).

## Consequences and validation

Iteration transitions no longer require editing agent instructions. Human and batch sessions share
rules without sharing a global execution cursor. Task allocation and integration remain the user's
or coordinator's responsibility; this change does not make unattended competing workers safe.

Validate index paths, skill metadata, generated instructions and affected repository verification.
Review discussion, explicit assignment and unassigned batch cases against the protocol. Runtime
coordination, recovery and multi-host claims require a later tool pilot; they are not validated here.
