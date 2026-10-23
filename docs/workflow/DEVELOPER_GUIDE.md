# Developer Guide

How to work in the muon platform workspace, for the human developer and for AI agents.
The decisions behind it are in [ADR-012](../adr/ADR-012_repository_baseline_and_workflow.md).
Procedures exist once, as skills in [`.agents/skills/`](../../.agents/skills/). This guide links to them.

## 1. New host setup

Toolchain: git, Python ≥ 3.9, [uv](https://docs.astral.sh/uv/), CMake ≥ 3.20, a C++17 compiler.

`muon` has two parts (ADR-012 §5):
- **launcher** (`muon-workspace`, installed once per host): finds the workspace you are in and runs
  *that workspace's* implementation;
- **implementation** (`platform/tools/muon`, pinned by each workspace's platform checkout): the real tool,
  run in its own uv environment. Never install it globally.

```sh
uv tool install vcs2l                       # provides `vcs`
uv tool install muon-workspace              # the launcher, from PyPI
muon ws init ~/src/muon_wkspc               # clones platform, then everything in platform/repos
cd ~/src/muon_wkspc && muon which           # launcher, workspace, implementation, data root
muon ws sync --legacy                       # optional: legacy references, cloned and locked
muon doctor
```

**Several workspaces on one host** are independent: each runs its own implementation, and has its own
settings in `<workspace>/.muon/workspace.yml` (not committed). To share the golden data instead of copying
it, run `muon ws init <dir> --data-root <existing>/testdata/golden`. `muon which` always tells you which
launcher, implementation and data root are in use. Outside any workspace, use `muon -C <dir> …`.

**Installing the launcher.** It is published on PyPI as `muon-workspace` and has no dependencies.
Upgrade it with `uv tool upgrade muon-workspace` when `muon doctor` says the workspace needs a newer one.
To release a new version: bump `version` in `tools/muon-workspace/pyproject.toml` and `__init__.py`, commit,
then push the tag `muon-workspace-v<version>`. The workflow `publish-muon-workspace.yml` tests the package and publishes it.

**AI tool setup per host.** `muon agents sync` generates the Claude and OpenCode adapters. Antigravity
(`agy`) needs a one-time entry in `~/.gemini/antigravity-cli/settings.json` under `permissions.allow`:
`read_file(<workspace path>)` (and the same path via any symlink you use), plus `command(muon status)`.
Codex needs nothing extra. Start it at the workspace root when a task spans several repositories.

**Golden test data** is local to each host and is not in git (ADR-011). Copy or move
`testdata/golden/` from another host (rsync), or set `data_root` in `.muon/workspace.yml`
(`MUON_DATA_ROOT` overrides it). `muon doctor` and `muon which` report where it looks.

## 2. Workspace layout

```text
muon_wkspc/            plain directory, no tool state
  AGENTS.md CLAUDE.md GEMINI.md   generated (muon agents sync)
  platform/  core/  contracts/  config/  testdata/  study/  tools/…
  legacy/<dir>/        read-only legacy references (locked)
  archive/<dir>/       host-local old trees (not managed)
  local.repos          optional per-host overrides (never committed)
```

The repository list is `platform/repos/workspace.repos` and `platform/repos/legacy.repos`. See them with `muon list`.

## 3. Daily loop

1. **Start:** read `## Next` in the active iteration's `platform/changes/<iteration>/tasks.md`,
   then run `muon status` (skill `muon-session`).
2. **Work in a repository.** Start the agent in that repository to keep it focused, or at the
   workspace root for cross-repository work.
3. **Verify:** `muon verify <repo>` (skill `muon-verify`).
4. **End:** update `## Next`, commit small and often, push the branch (`wip/<topic>` is fine).

Commands: `muon status`, `muon verify [repo…]`, `muon branch <name> <repo…>`,
`muon ws sync [--update]`, `muon freeze`, `muon doctor`, `muon testdata …`.

`muon ws sync --update` only fast-forwards repositories that are clean and on their pinned branch.
It never rewrites your work.

## 4. Cross-repository changes

While prototyping (ADR-012 §6):
- Use the same branch name in each repository: `muon branch <topic> core platform`.
- Agents may edit any repository, but must **announce** every repository they touched outside their starting one.
- Contracts used only by core stay in core and change in the same commit as their consumer.
- System contracts are drafted in `core/contracts/system/`. Record notable decisions in `docs/decisions.md`.
- Run `muon status` before pushing, so that no repository is left dirty or on an unexpected branch.

A change proposal (`changes/`, skill `muon-new-change`) is optional. Write one to record a decision, or
to promote a prototype into the spec baseline (ADR-010).

## 5. Prototype → baseline

Prototype freely inside a repository (ADR-010 prototype lane). When the behaviour should become
the baseline:
1. write the specification delta;
2. give the tests requirement IDs;
3. record the decision.

Domain iterations follow skill `muon-domain-iteration`. Legacy analysis follows skill `muon-legacy-archaeology`.

## 6. Snapshots and releases

`muon freeze -o <file>` records exact SHAs of every repository (vcs2l format). Data products
record the core SHA and the conditions snapshot (ADR-012 §10). Instrument release BOMs start with
the first instrument release (ADR-012 §6).

## 7. Adding repositories

Skill `muon-new-project`. Apply the split test (ADR-012 §3): a new repository is justified only when
the toolchain, lifecycle or audience differs. Otherwise add a directory to an existing repository. Add the
repository to `platform/repos/workspace.repos`, and give it `.muon/repo.yml` and `AGENTS.md` (template:
`templates/project/`).

## 8. Legacy references

- `muon ws sync --legacy` clones the missing legacy references and locks all of them: the tree is read-only,
  pushes are disabled, and refusing hooks are installed. `muon legacy status` shows the lock state.
- **Never** edit, `chmod`, commit, push or build inside `legacy/` or `archive/`. To run legacy code,
  build out of tree in `$(muon legacy build-dir <name>)`.
- Adding a legacy reference: an entry in `platform/repos/legacy.repos` with
  `muon: {maturity: legacy, informs: [...]}`, and a row in [legacy_inventory.md](../legacy_inventory.md).
  Trees without a remote go to `archive/` (host-local, not managed).

## 9. Working with AI agents

- **Rules:** each repository's `AGENTS.md` (short, always loaded) plus `platform/AGENTS.md`, and
  skills loaded on demand. `CLAUDE.md`/`GEMINI.md` are shims. `muon agents sync` regenerates the
  shims, skill links and tool adapters; `muon agents adapters` lists the per-tool status.
- **Keep the rules lean.** `muon doctor` checks the size limits. Put details in skills or docs.
- **One fact, one home.** Decisions go in `docs/decisions.md` or an ADR; work in progress goes in `tasks.md` `## Next`.
  Tool memories are caches only.
- **Parallel agents:** use different repositories, or a git worktree of the one repository involved.
- **Review diffs, not prose.** Agents propose; you merge. Agents never push, create remotes or
  delete branches without your confirmation.
- **Fresh-session check:** occasionally start a new session (in each AI tool you use) with a small task in
  `core/`. It should follow the session protocol and verify before finishing.

## 10. Hardening

When a trigger in ADR-012 §6 fires (second domain, first release, second developer, …), add the
listed mechanism and record it in `docs/decisions.md`.
