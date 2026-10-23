# Workspace reorganization: domain repositories, vcs2l + muon CLI, staged rigor

Status: verified (cut over 2026-10-23); WS-008 fresh-session check pending
Owner: project owner
Decision record: [ADR-012](../../docs/adr/ADR-012_repository_baseline_and_workflow.md) (approved in discussion, 2026-10-23)
Affected repositories: platform, core (new `ufan/muon_core`), contracts, testdata; retired: `ufan/muon_daq`
Requirements: `WS-001` … `WS-008` (specs.md)

## Why

See ADR-012 §2. In short:
- one developer working with AI agents in early prototyping needs low friction;
- hardware domains have separate lifecycles, so there is one repository per domain plus an instrument layer;
- west was used beyond its design.

## What changes

- **core:** `ufan/muon_core` holds the DAQ and contracts histories. This reuses the history-preserving import
  from the earlier hybrid-core attempt, branch `migration/hybrid-core` (commits up to `01b331f`).
  On top of that import:
  - west is removed;
  - contracts are split into `science/` and `system/`;
  - `AGENTS.md` files are trimmed;
  - `.muon/repo.yml` is added.
- **contracts:** becomes a placeholder for system contracts (README states the extraction trigger).
- **testdata:** west extension removed; `muon testdata` passes through to `tools/testdata.py`.
- **platform:**
  - `west.yml` and the west extensions are removed; `repos/*.repos` and `tools/muon` (the CLI, with tests) replace them;
  - lean `AGENTS.md`, with the moved content in `docs/engineering_context.md`;
  - new docs: ADR-012, `docs/decisions.md`, `docs/workflow/DEVELOPER_GUIDE.md` (replaces WORKSPACE_GUIDE);
  - skills: `muon-session` added, `muon-bump-manifest` removed, the others updated;
  - ADR-006/009/010/011, LANDSCAPE, the legacy inventory and the DAQ iteration records amended.

## Superseded work

The Codex "hybrid-core" migration (`.migration/hybrid-core/`, platform branches `migration/hybrid-core` and
`workflow/solo-validation`, local `instrument` prototype) is superseded by this change, at the owner's request
on 2026-10-23. Its core import commits are reused. Its west-based platform changes and its ADR-012/013 drafts are
not merged. Its remote branches are left untouched; deleting them needs the owner's confirmation.

## Cutover (needs confirmation; see tasks.md)

1. Push the `reorg/workspace` branches. Merge to `main` in core, platform, contracts and testdata.
2. Build the new workspace side by side: `muon ws init <new>`. Move `testdata/golden/` (~85 GB, so move it,
   don't copy) and `archive/` across; then `muon ws sync --legacy`, `muon doctor`, and swap the directories.
3. Retire `ufan/muon_daq`: a pointer commit, then archive it on GitHub. Its `pre-reorg` tag marks the final state.

## Rollback

`pre-reorg` tags in platform, contracts, daq and testdata, plus `pre-reorg.repos` (exact SHAs). The old
workspace is kept until the owner confirms the new one.
