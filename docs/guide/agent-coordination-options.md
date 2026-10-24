# Existing options for agent coordination

Status: reference (dated research, not an adoption decision).

Research date: 2026-10-24. Documentation review only; no tools were installed or exercised.
These are open-source candidates with visible GitHub communities, not a benchmark or an adoption
commitment. Features below are documented project capabilities; Muon fit is our assessment.

## Shortlist

| Candidate | Documented capabilities and license | Assessment for Muon |
|---|---|---|
| [Agent Orchestrator / Orchestrator.inc](https://github.com/OrchestratorInc/agent-orchestrator) (formerly under ComposioHQ) | Apache-2.0. Worker-specific branches/worktrees, multiple coding agents, project planning and supervision, PR/CI/review visibility. [Project README](https://github.com/OrchestratorInc/agent-orchestrator#readme). | First candidate to pilot for human planning plus parallel coding sessions. Validate headless batch operation, Linux deployment and multi-repository assignments rather than assuming its repository-oriented model matches this workspace. |
| [Beads](https://github.com/gastownhall/beads) | MIT. Dolt-backed dependency graph, ready-work discovery, JSON output and an atomic task-claim command; CLI/agent integrations. [Project README](https://github.com/gastownhall/beads#readme). | Candidate if dependency-aware task ownership is the missing piece. It is task state infrastructure, not a complete worker runner/integrator. Dolt adds an operational dependency. Atomic claims against one store do not by themselves prove exclusive claims across disconnected replicas; validate topology and synchronization. |
| [Gas Town](https://github.com/gastownhall/gastown) | MIT. Multi-agent workspace manager with coordinator/worker roles, Beads tracking, persistent handoffs, watchdogs and per-repository merge queues. [Project README](https://github.com/gastownhall/gastown#readme). | Closest to a fuller coordination system, including multiple repository containers. Its workspace layout, supporting services and automatic integration need evaluation against Muon's manifests, immutable references and owner approval gates. More machinery than the current need. |
| [LangGraph](https://github.com/langchain-ai/langgraph) | MIT. General orchestration runtime with persistence, durable execution and human intervention. [Official overview](https://docs.langchain.com/oss/python/langgraph/overview). | A building block if we eventually need a custom scientific/hardware approval workflow. Not a ready-made coding worktree/task integration system; using it first would leave substantial infrastructure to build. |

## Recommendation

Keep the lightweight [work discovery and assignment protocol](../../work/README.md) now. Before
building a queue, lease service or scheduler in `muon`, pilot Agent Orchestrator for a complete
coding-session workflow, or Beads if the immediate gap is task tracking and claims. Evaluate Gas
Town when sustained autonomous coordination and integration justify a broader workspace manager.
Use LangGraph only if demonstrated requirements remain unmet by existing tools.

Keep reviewed scientific plans, specs, approvals and architectural decisions in their current
repositories. An adopted runtime can own attempts, claims and worker status; avoid maintaining
competing authoritative task statuses in both Markdown and a runtime. Reference stable task IDs
and link plans to runtime tasks when introducing such a system.

## Pilot acceptance criteria

Use disposable repositories and harmless tasks before connecting the live workspace:

- Run a human discussion session alongside two assigned workers in isolated checkouts.
- Demonstrate task dependencies, bounded batches and an explicit unassigned/blocked outcome.
- Restart a worker; inspect recovery, duplicate execution and stale ownership behavior.
- For multi-host scheduling, test simultaneous claims against the actual shared-store topology;
  offline replica merges are not a distributed mutual-exclusion guarantee.
- Verify cross-repository task context and a consistent branch name, without assuming atomic merges.
- Enforce Muon's verification commands, human approval gates and confirmation before pushing;
  disable default auto-merge/push behavior where required.
- Preserve legacy and golden data protection; inspect instruction-file modifications made by installers.
- Record exact tool versions/licenses, runtime costs and host requirements during the pilot.

Adoption should be a separate scoped decision after this evidence, not a prerequisite for today's
work-index improvement. No runtime task store, scheduler or tool installation is introduced here.
