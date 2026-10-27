---
name: muon-session
description: Orient and hand off muon workspace sessions, including discussion, directed changes and assigned batch work, across AI tools and hosts.
---

# Session start and handoff

## Start

1. Read the workspace rules in `platform/AGENTS.md` and the scope protocol in
   `platform/work/README.md`. Follow the explicit user/coordinator assignment first. Otherwise use
   `platform/work/index.yml` for orientation; it is not a work queue or authorization to implement.
2. For assigned iteration work, read the linked proposal and relevant tasks, including `## Next`.
   For discussion or unrelated maintenance, read only relevant context; do not adopt an iteration.
   An unattended batch session without a bounded assignment reports that it is unassigned and stops.
3. Before mutations, run `muon status` and note dirty, ahead/behind or off-pin repositories. Inspect
   branch state as needed for read-only work. Do not fetch, switch or alter other sessions' work
   merely because it exists; retrieve a remote branch only when required by the assignment.
4. Skim the active entries in `platform/governance/decision_log.md`. For substantial work, briefly
   explain the scope and next action. Discussion can proceed directly to answering the user.

## During the session

- Respect the request's intent: discussion and backup do not authorize iteration implementation.
- Act within your assigned role. Never review or approve work you authored.
- Announce each additional repository changed. Use the same task branch name across changed repos.
- Concurrent writers use isolated worktrees/checkouts; the index provides no claims or locks.
- Record agreed durable decisions in an ADR, or in `platform/governance/decision_log.md` if they pass its log
  test. A document edit with a clear commit message is the record for decisions that document captures.

## End

1. For changed repositories, run `muon verify <repo>` (skill `muon-verify`), inspect the scoped diff
   and commit only this session's changes, in the commit format of
   `governance/engineering_process.md` §4. No mandatory writes or commits for discussion alone.
2. Hand off to the destination specified by the assignment, according to your role (engineering
   process §7). Workers report task ID, commits, verification, blockers, proposed `show` decision requests
   and pending approvals; only the integrator updates shared summaries and the decision requests.
   For human-directed iteration work, keep its `tasks.md` `## Next` focused on pending actions,
   questions and hardware validation limits. Unrelated maintenance needs no iteration update.
3. Report what was verified and what was not. Push only with the user's confirmation.
4. Tool-specific memory is a cache, not the only durable record of decisions or implementation work.
