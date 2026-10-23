# Tasks

| # | Repo | Task | Spec IDs | Verification | Status |
|---|---|---|---|---|---|
| 1 | all | `pre-reorg` tags, `pre-reorg.repos` snapshot | — | `git tag -l pre-reorg` | done (tags pushed) |
| 2 | platform | `tools/muon` CLI + tests; `repos/*.repos`; `.muon/repo.yml` | WS-001 | `muon verify platform` | done |
| 3 | core | Base on `migration/hybrid-core`; drop west; science/system contracts; lean rules; metadata | WS-002…WS-004 | `muon verify core` | done |
| 4 | contracts, testdata | Placeholder for contracts; testdata without west | WS-002 | `muon verify testdata` | done |
| 5 | platform | ADR-012, decisions log, DEVELOPER_GUIDE, lean AGENTS.md, skills, ADR amendments | WS-005, WS-008 | `muon doctor` | done |
| 6 | all | Per-repository CI (GitHub Actions running the verify command) | WS-003 | first CI run green | done |
| 7 | all | Push `reorg/workspace`, merge to `main`; `muon_core` default branch → `main` | — | `muon status` clean | done 2026-10-23 |
| 8 | host | New workspace via `muon ws init` (platform, core, contracts cloned from GitHub; testdata, config, study, tools, legacy, archive moved), swap | WS-001, WS-006, WS-007 | `muon doctor` clean, `muon verify` pass | done 2026-10-23; old tree in `../muon_wkspc.old` (daq, west state) |
| 9 | GitHub | Retire `ufan/muon_daq` (pointer commit + archive); delete hybrid-core branches, worktree and `.migration/` | — | — | done 2026-10-23 |

## Next

- Run a fresh-session check in `core/` with Claude Code and Codex (WS-008).
- Delete `../muon_wkspc.old` once the new workspace is confirmed (it holds only the old `daq/` clone, `.west/`
  and copies of repos that are pushed).
