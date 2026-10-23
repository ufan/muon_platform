# Tasks

| # | Repo | Task | Spec IDs | Verification | Status |
|---|---|---|---|---|---|
| 1 | all | `pre-reorg` tags (local), `pre-reorg.repos` snapshot | — | `git tag -l pre-reorg` | done (tags not pushed) |
| 2 | platform | `tools/muon` CLI + tests; `repos/*.repos`; `.muon/repo.yml` | WS-001 | `muon verify platform` | done |
| 3 | core | Base on `migration/hybrid-core`; drop west; science/system contracts; lean rules; metadata | WS-002…WS-004 | `muon verify core` | done |
| 4 | contracts, testdata | Placeholder for contracts; testdata without west | WS-002 | `muon verify testdata` | done |
| 5 | platform | ADR-012, decisions log, DEVELOPER_GUIDE, lean AGENTS.md, skills, ADR amendments | WS-005, WS-008 | `muon doctor` | done |
| 6 | all | Per-repository CI (GitHub Actions running the verify command) | WS-003 | first CI run green | done (runs after push) |
| 7 | all | Push `reorg/workspace`, merge to `main` | — | `muon status` clean | **needs confirmation** |
| 8 | host | New workspace side by side, move golden data + archive, `muon doctor`, swap | WS-001, WS-006, WS-007 | `muon doctor` clean | **needs confirmation** |
| 9 | GitHub | Retire `ufan/muon_daq` (pointer commit + archive); decide what to do with the hybrid-core branches | — | — | **needs confirmation** |

## Next

- Owner: review the four `reorg/workspace` branches (core, platform, contracts, testdata), then confirm tasks 7–9.
- After cutover, run a fresh-session check in `core/` with Claude Code and Codex (WS-008).
