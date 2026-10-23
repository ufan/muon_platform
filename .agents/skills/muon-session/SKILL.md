---
name: muon-session
description: Use at the start and at the end of every work session in the muon workspace, in any AI tool and on any host. Loads where the work stands and hands it off through git (ADR-012 §8).
---

# Session start and handoff

## Start

1. Find the current iteration in `platform/AGENTS.md` ("Current iteration") and read `## Next` in
   `platform/changes/<iteration>/tasks.md`.
2. Run `muon status`. Note repositories that are dirty, ahead, behind or off their pinned branch.
   If the work is on a `wip/<topic>` branch on another host, fetch it first.
3. Skim `platform/docs/decisions.md` (newest first) for decisions since the last session.
4. Tell the user in one short paragraph where things stand and what you plan to do next.

## During the session

- Announce each repository you change outside the one you started in. Use the same branch name in each (`muon branch`).
- Record small decisions in `platform/docs/decisions.md` as you make them: one dated line each.

## End

1. Run `muon verify <repo>` for every repository you changed (skill `muon-verify`).
2. Update `## Next` in the iteration's `tasks.md`:
   - what was done;
   - what is next;
   - open questions;
   - which hardware tests were and were not run.
3. Commit in each changed repository (small commits, clear messages).
4. Ask the user before pushing. Unpushed work does not reach other hosts.
5. Tool-specific memory is optional. Never let it be the only record.
