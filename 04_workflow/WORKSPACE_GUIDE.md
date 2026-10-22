# Workspace Guide

Status: normative procedures. The decisions behind them are in
[ADR-009](../03_adr/ADR-009_workspace_repository_model.md) (workspace, repositories, agents, legacy)
and [ADR-010](../03_adr/ADR-010_spec_driven_domain_iteration.md) (spec-driven iteration, prototype lane).

West is the single interface for workspace features. The muon commands (`west catalog`,
`west verify`, `west agents-sync`, `west xbranch`, `west refs`, `west testdata`) are west
extensions provided by the hub and by `testdata`.

## 1. When west is required

- **Workspace features need west:** legacy references, agent files and skills, the catalog, verify,
  cross-repository branches, pinned revisions and release snapshots, test data.
- **Building and testing one repository does not.** A plain `git clone` plus the repo's own build is
  enough, and each repo's verify command never calls west. A plain clone simply has none of the
  workspace features.

Install west once per machine: `uv tool install west` (or `pipx install west`).

## 2. Workspace shapes

| Shape | Create | Use when |
|---|---|---|
| Full | `west init -m git@github.com:ufan/muon_platform.git --mr main ws && cd ws && west update` | Platform and integration work, several domains |
| Repo-rooted | `west init -m git@github.com:ufan/muon_daq.git --mr prototype/fx3-gen1 ws && cd ws && west update` | Developing one domain on its own, with the dependencies, legacy references and hub tooling its own `west.yml` declares (ADR-009 §13) |

Both produce the same relative layout (`<top>/daq`, `<top>/contracts`, `<top>/legacy/<dir>`), so
paths in `AGENTS.md` files are valid in either. After setup, run `west refs sync` (legacy references)
and `west agents-sync` (agent files).

Partial workspaces: `west config manifest.group-filter -- -research,-tools`, then `west update`.

## 3. Daily use

- `west catalog [-a] [-g GROUP]`: projects with maturity, role, groups, `reference_for`.
- `west update <project>`: **only** when that project is clean and pushed. It checks out the pinned
  revision as a detached HEAD; leave it with `git switch <branch>`, or use `west update -k` to keep a
  descendant branch. Never on legacy projects (§6).
- `west xbranch <topic> <projects…>`: the same topic branch in several repositories (ADR-009 §8).
- `west verify [<projects…>|-g GROUP]`: runs each project's plain `userdata.verify` command.
- `west agents-sync [--check]`: regenerates agent files after rule, skill or manifest changes.
- Manifest changes (revision, remote, maturity, groups): skill `muon-bump-manifest`.

## 4. Adding a new repository

Skill: `muon-new-project`.

1. **Split rule** (ADR-009 §4). There must be a different lifecycle, toolchain, deployment target or
   audience. Otherwise add a directory to an existing repository.
2. **Create** `ufan/muon_<name>` on GitHub (a human, or `gh repo create` with approval).
3. **Skeleton:** copy [`templates/project/`](../templates/project/) and fill in the placeholders.
4. **Verify command:** a plain shell command, run from the repo root, that never calls west.
5. **Declare** the project in `platform/west.yml`:
   ```yaml
   - name: <name>
     repo-path: muon_<name>
     path: <name>
     revision: main
     groups: [<online|offline|...>]
     userdata: {role: ..., maturity: incubating, deploy: <edge|server|dev>, spec: <name>/SPEC.md, verify: <cmd>}
   ```
   Optionally, the repository carries its own `west.yml` (from `west.yml.example`) for its
   dependencies and single-owner legacy references (ADR-009 §13).
6. **Check:** `west catalog -a`, then `west verify <name>`, then `west agents-sync`.
7. **Commit** the manifest change in `platform` with the reason. Push after review.

## 5. Adding a legacy repository

1. **Naming:** path `legacy/<dir>`, name `<dir>-legacy` (underscores become dashes), `groups: [legacy]`,
   `userdata: {maturity: legacy, reference_for: [...], role: ..., spec: platform/legacy_inventory.md}`.
2. **Remote and revision:** keep the original remote (non-GitHub remotes are allowed for legacy).
   Pin a fixed revision, preferably a tag `legacy-final`.
3. **Where to declare:** in the single repository that uses it (its `west.yml`), or in
   `platform/west.yml` when several repositories use it.
4. **No remote?** West has no local-only project type. Every project needs a URL, used only
   to clone and fetch. Choose one of two:
   - **Give it a URL:** push it to a private `ufan/muon_legacy_<dir>`, or to any git URL such as a
     lab server or a file URL. It then becomes a normal legacy project (steps 1–3, 5).
   - **Keep it host-local:** do not add it to any manifest. Record it in the inventory's
     "Host-local references" table. It is not fetched or L1-locked, and other workspaces won't have it.
     The read-only rule (L2) still applies. Non-git trees are always host-local.
5. **Fetch and lock:** `west refs sync <dir>-legacy`, then `west refs status`, then `west agents-sync`.
6. **Inventory:** add a row to [`legacy_inventory.md`](../legacy_inventory.md).

## 6. Using legacy references

- `west refs sync`, run from inside a project, fetches and locks the legacy refs whose
  `reference_for` names that project. Other forms: `--all`, or explicit names.
  `refs sync --update` moves *clean* checkouts to the pinned revision and relocks them.
- `west refs status` shows LOCKED or UNLOCKED, push disabled, hooks present, and pinned revision.
- **Never** `west update` a legacy project, unlock it by hand, `chmod` it, edit it, commit or push in
  it, or build inside it.
- Running legacy code (golden data): build out of tree in `$(west refs build-dir <name>)`.
- The three guardrail layers (ADR-009 §15) apply in every shape:
  - **L1:** read-only on disk, push disabled, refusing hooks.
  - **L2:** `AGENTS.md` instructions.
  - **L3:** tool adapters.

## 7. AI coding tools

- **Canonical and committed:** `AGENTS.md` per repository, and skills in `platform/.agents/skills/muon-*`.
- **Generated:**
  - `CLAUDE.md`/`GEMINI.md` shims;
  - the root `AGENTS.md`;
  - skill links in `.agents/skills/` and `.claude/skills/` at the root and in every project;
  - tool adapters.

  Check them with `west agents-sync --check`. The per-tool adapters are listed in ADR-009 §14.
  Per-project files are generated only for `incubating`/`active`/`stable` projects (and for the
  manifest repository of a repo-rooted workspace). `reference` and `legacy` projects are left untouched.
  A repo-rooted workspace gets the skills and platform rules when its `west.yml` lists `platform`
  as a plain project (as `daq` does).
- **Start any tool anywhere:** at the workspace root (platform-level work) or inside a project (domain
  work). The tool sees the project rules, the platform rules (directly or via pointer), the playbook
  skills, and read-only legacy references.
- **Adding a new tool:** add its shim or adapter in `scripts/west_commands/muon_ws/agents.py` and its row to ADR-009 §14.
  Canonical files do not change.

## 8. Test data

Test datasets are managed by the self-contained `testdata` project (ADR-011). All procedures are in
`testdata/README.md`: referencing `id@version`, pinning in `tests/golden.yml`, add, modify, retire, prune.
Use `west testdata ...`. A testdata-only workspace: `west init -m git@github.com:ufan/muon_testdata.git ws`.

## 9. Lifecycle

| Change | How |
|---|---|
| Promote maturity (`incubating → active → stable`) | edit `userdata.maturity`, commit the manifest (`stable` requires semver-managed contracts) |
| Retire a domain into legacy | tag `legacy-final`, move to `legacy/<dir>`, rename `<dir>-legacy`, set maturity and `reference_for`, `west refs sync`, update the inventory (ADR-010 §4 step 8) |
| Migrate a remote (e.g. gitee → GitHub) | change `remote:` (and `repo-path:`), commit the manifest |
| Rename or remove a project | edit the manifest(s), then `west agents-sync`. Remove stale directories by hand after checking for local work |
| Enable a repository manifest import | after the repository is pushed and `west update -k <project>` has run once: replace its `groups:` with `import: {name-blocklist: [platform]}`, and remove hub entries the repository now declares (ADR-009 §13) |
