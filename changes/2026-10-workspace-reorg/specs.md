# Spec deltas

Area `WS` covers the workspace and repository model (ADR-012).

## ADDED

### WS-001 Workspace from repos files
`muon ws init <dir>` creates a workspace from `platform/repos/workspace.repos`. Legacy references are
cloned and locked only on request. Acceptance: `platform/tools/muon/tests` (`test_init_*`, `test_legacy_*`) pass.

### WS-002 No west at the muon level
No platform, core, contracts or testdata file requires west. Acceptance: `grep -rn "west " --include=*.md`
in these repositories finds only historical or explanatory text (ADR-009 header, ADR-012, decisions log).

### WS-003 Core builds from a plain clone
Acceptance: `cmake --preset dev && cmake --build --preset dev && ctest --preset dev` passes in a fresh
clone of core. CTest label `WS-003`.

### WS-004 Core package is consumable
An installed and relocated `MuonCore` package is found by a consumer, and unimplemented components are
rejected. Acceptance: CTest label `WS-004`.

### WS-005 Lean rules
`platform/AGENTS.md` is ≤ 3500 bytes, and the `AGENTS.md` of every dev repository is ≤ 2500 bytes.
Acceptance: `muon doctor` reports no size violations.

### WS-006 Agent files generated for every tool
Acceptance: `muon agents sync --check` exits 0 in the workspace.

### WS-007 Legacy guardrails unchanged
Acceptance: `muon legacy status` shows every cloned legacy reference as LOCKED.

### WS-008 Continuity in git
The session protocol (skill `muon-session`), `docs/decisions.md` and `tasks.md` `## Next` exist and are
referenced from `platform/AGENTS.md`. Acceptance: review, plus a fresh-session check with two AI tools.

## MODIFIED

ADR-009 (§1–§4, §6–§10, §12, §13 superseded), ADR-010 (prototype lane by default), ADR-011 (several hosts),
ADR-006 §2, PLATFORM_ARCHITECTURE §16, LANDSCAPE, legacy inventory, DAQ iteration 1 records.

## REMOVED

`platform/west.yml`, `platform/scripts/` (west extensions), `docs/workflow/WORKSPACE_GUIDE.md`,
skill `muon-bump-manifest`, `templates/project/west.yml.example`, `core/west.yml`, `testdata/west.yml`
and its west extension.
