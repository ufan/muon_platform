# ADR-009 Workspace and Repository Model

Version: 1.0
Status: Partly superseded by [ADR-012](ADR-012_repository_baseline_and_workflow.md) (2026-10-23)
Supersedes: ADR-006 §2 "Repository Organization"
Related: ADR-004 (version model), ADR-006 (AI workflow), ADR-010 (spec-driven domain iteration)
Revised: 2026-10-21 (§3, §5 legacy location; §12–§15 added); 2026-10-22 (`west legacy`, `archive/`, `informs`, maturity `support`)

> **2026-10-23: West is no longer the workspace interface.** ADR-012 supersedes §1–§4, §6–§10, §12 and §13:
> one repository per domain (`muon_core` is the scientific domain), vcs2l `.repos` files plus the `muon`
> CLI, and staged rigor. The following remain in force, with `muon` replacing the west commands
> (`west legacy …` → `muon ws sync --legacy` / `muon legacy …`, `west agents-sync` → `muon agents sync`):
> §5 maturity levels and legacy/archive locations, §11 consequences of a multi-repository model,
> §14 tool-neutral agent setup, §15 legacy guardrails. The text below is kept for history.

## 1. Decision Summary

The platform is developed as a **multi-repository workspace coordinated by
[west](https://docs.zephyrproject.org/latest/develop/west/index.html)** in a
"star" topology:

- One **hub repository** (`platform`) is the west manifest repository *and* the
  specification hub: requirements, architecture, ADRs, change proposals,
  agent rules, and workspace tooling.
- Every component (DAQ, contracts, preprocess, recon, ...) is a **west
  project**: an independent git repository with its own history, branches,
  and release cycle.
- The hub's `west.yml` pins a compatible revision of every project. A frozen
  manifest (`west manifest --freeze`) is the software bill of materials (BOM) of a platform state.

## 2. Context

- The platform has many components with different lifecycles, toolchains,
  and deployment targets (ARM64 edge vs. server vs. lab).
- Components share contracts (wire protocol, EDM, file formats) and form one
  application chain.
- The team is small (1–3 developers) and relies on AI coding agents working
  both across the whole system and inside a single component.
- Development is bottom-up, one domain at a time, starting from legacy code
  used as reference (see ADR-010).

Options considered: a single monorepo, git submodules under an umbrella repo,
package-only integration (Conan/conda/Debian), and manifest-based workspaces
(Google `repo`, west, jiri, gclient, vcstool, kas). West was chosen because it
offers project groups, manifest imports, pinned revisions, frozen snapshots,
per-project metadata (`userdata`), and Python extension commands. It is also
proven in commercial products, for example the nRF Connect SDK, whose code repo
doubles as its manifest repo.

## 3. Workspace Layout

```text
<workspace>/                 west topdir (.west/)
  AGENTS.md CLAUDE.md GEMINI.md  generated (§14)
  .agents/skills/muon-*  .claude/skills/muon-*   generated skill links (§14)
  platform/                  hub: west.yml, AGENTS.md, changes/, templates/, scripts/ (west extensions), .agents/skills/,
                             docs/ (requirements, architecture, adr, workflow, guide; reading order in docs/README.md)
  contracts/                 wire / pipeline / persistence / api / fsm schemas (versioned independently)
  daq/                       acquisition service (active); carries its own west.yml (§13)
  config/  study/  tools/...
  legacy/                    managed legacy projects: in a manifest, locked read-only (§5, §15)
    muon400_process/  analysis/  usb_app2/     west projects (L1-locked)
  archive/                   host-local trees: not in any manifest, this host only (§5; L2 only)
    imaging/  frame/
```

`west.yml` in the hub is the authoritative list of projects. Directory
names in the workspace are project paths, not architecture.

## 4. Repository Split Rule

Create a separate repository only when the part differs in at least one of:

1. **lifecycle**: release cadence or stability expectations
2. **toolchain**: e.g. FPGA/MCU firmware vs. Linux C++ vs. Python analysis
3. **deployment target**: edge appliance vs. server vs. developer machine
4. **audience/ownership**: partners, researchers, operators

A different *domain* alone is not a reason to split. While contracts between
two parts still churn, prefer keeping them together. West makes merging or
extracting repositories later cheap.

## 5. Maturity Levels and Groups

Every project declares `userdata.maturity`:

| Level | Meaning | Agent rules |
|---|---|---|
| `legacy` | old implementation, reference only | read-only; never a dependency |
| `support` | useful data/tools, not on the production path (config, studies, tools, test data) | modify only on explicit request |
| `incubating` | new, contracts provisional | spec-driven, breaking changes allowed with a change proposal |
| `active` | domain currently in its iteration | spec-driven, full verification |
| `stable` | contracts frozen, semver-managed | breaking changes require an ADR |

**Legacy location.** Legacy repositories live centrally in `legacy/<dir>`, with west
name `<dir>-legacy` (underscores become dashes), group `legacy`, maturity `legacy`, and an
explicit `userdata.informs` listing the projects they inform. They are never nested
inside an active repository. Legacy projects inform many projects, a nested clone would
pollute the active repo's working tree, and agents and code search would treat legacy code
as part of the active project. Hardware and vendor *source-of-truth* material (e.g.
`daq/ref/`) is not legacy and stays inside its repository.

**Archive location.** Old trees that have no remote (or are not git at all) and are kept on one
host only go to `archive/<dir>`, never into `legacy/`. They are not in any manifest, are recorded
in `docs/legacy_inventory.md`, and are protected by the rules (L2) only. Directory alone tells the
two kinds apart: `legacy/` = managed and reproducible, `archive/` = host-local.

Groups select partial workspaces: `online`, `offline`, `config`, `contracts`,
`research`, `tools`, `legacy`. The default `group-filter` disables `legacy`;
enable it with `west update --group-filter=+legacy`, or per workspace with
`west config manifest.group-filter +legacy`.

## 6. Remote Policy

- **GitHub is the default remote** for all active and new work.
- Legacy and support projects may keep other remotes (e.g. gitee) declared
  per project in `west.yml`.
- Migrating a project means changing its `remote:` line in `west.yml` and
  merging that through a manifest PR.

## 7. Contracts

> Superseded by [ADR-012](ADR-012_repository_baseline_and_workflow.md) (2026-10-23); kept for history. Current: [repository model](../architecture/repository_model.md#contract-ownership).

`contracts` is a separate repository and the single source of truth for
contracts that cross repository boundaries: pipeline records, persistence formats,
service APIs, and state machine tables. Device ↔ host wire protocols are **not**
in `contracts`. Only DAQ talks to the hardware, so they are owned by the DAQ hardware
references, one per target (`daq/ref/<type>/<generation>/`; decided 2026-10-22). It is versioned with semver (`0.x` while provisional).
Producers and consumers depend on the revision pinned in `west.yml`, never
on a copied or vendored version.

## 8. Cross-Repository Change Protocol

> Superseded by [ADR-012](ADR-012_repository_baseline_and_workflow.md) (2026-10-23); kept for history. Current: [developer guide §4](../workflow/DEVELOPER_GUIDE.md#4-cross-repository-changes).

A change touching several projects:

1. A change proposal is opened in the hub `changes/` (ADR-010).
2. The same topic branch name is used in every affected project
   (`west xbranch <name>`).
3. Each project gets its own PR or commit series.
4. A **manifest PR** in the hub moves the affected `revision:` entries to the
   new commits or tags. Integration verification (`west verify`) runs against that
   manifest state.
5. Contract changes merge first; consumers follow.

## 9. Releases and Provenance

- A platform state is identified by the hub commit plus
  `west manifest --freeze` output (all projects at exact SHAs).
- This frozen manifest is the *software* component of ADR-004 §7's
  instrument version. Firmware, calibration and configuration versions are
  recorded alongside it.
- Scientific products record the frozen-manifest identifier as provenance.

## 10. Planned Projects

Created only when their domain iteration starts (ADR-010):
`recon`, `imaging`, `sim`, `conditions` (geometry, mapping, calibration with
validity intervals), `firmware`, `ux`.

## 11. Consequences

Positive:
- Independent component histories and cycles. Partial checkouts by group.
- One versioned place (the hub) for specs, rules and system catalog,
  visible to AI agents at both workspace and component level.
- Reproducible platform snapshots that match ADR-004.

Negative / mitigations:
- No atomic cross-repo commits. Mitigated by the change protocol (§8) and by
  keeping co-evolving parts in one repo (§4).
- West does not build. Each project declares a `userdata.verify` command, and
  build integration (CMake package exports) is added per project.
- `west update` rewrites checkouts. Run it only on clean, pushed projects.

## 12. West Usage Policy

> Superseded by [ADR-012](ADR-012_repository_baseline_and_workflow.md) (2026-10-23); kept for history. Current: `muon` CLI and vcs2l `.repos` files ([developer guide](../workflow/DEVELOPER_GUIDE.md)).

West is required only at the **workspace** level: setting up or updating a multi-repository
workspace, the catalog, pinning revisions and releases, cross-repository branches, and
generating agent files. It is **never** required to build, test, run or develop inside a
repository. Every repository works from a plain `git clone`. Its `userdata.verify` is a
plain shell command run from the repository root, and its agent rules degrade gracefully
when `../platform` is absent.

West is the **single interface** for workspace features. Single-repository work uses a
repo-rooted workspace (§13), not a bare clone with a separate tool. The muon commands are west
extensions. Their implementation is the internal Python package
`platform/scripts/west_commands/muon_ws`, which is not a user-facing tool. (Revised 2026-10-22: an earlier
standalone `muon-ws` CLI was dropped to keep one entry point.)

Procedures: `docs/workflow/WORKSPACE_GUIDE.md` (retired; current procedures are in the [developer guide](../workflow/DEVELOPER_GUIDE.md)).

## 13. Repository-Owned Manifests

> Superseded by [ADR-012](ADR-012_repository_baseline_and_workflow.md) (2026-10-23); kept for history. Current: `platform/repos/*.repos` and each repository's `.muon/repo.yml` ([repository model](../architecture/repository_model.md)).

A repository may carry its own `west.yml` that declares what *it* needs: its dependencies
(e.g. `contracts`), the hub as a plain project (for docs, skills and extensions), and the
legacy projects only it uses.

- **Ownership rule.** A legacy project used by exactly one repository is declared in that
  repository's manifest. One used by several repositories is declared in the hub.
- **Import.** The hub imports repository manifests (`import: true`). West keeps the first
  definition of a project name, and the hub's own entries come first, so the hub can
  override or pin anything a repository declares.
- **No cycles.** A repository manifest never imports the hub. Listing it as a plain project is allowed.
- **Same remotes.** Remote names and URLs are identical in the hub and repository manifests.
- **Repo-rooted workspace.** `west init -m <repo url>` produces a workspace with the same
  directory layout as the full one, so paths in rules files stay valid.
- **Hub entry shape (verified with west 1.5).** The hub's entry for an importing project uses
  `import: {name-blocklist: [platform]}`, because the repository manifest lists the hub as a
  plain project and the hub's path is taken by the manifest repository. The entry **cannot
  carry `groups`**, because west forbids `groups` together with `import`. Such a project is
  therefore always active and is selected by name (`west verify daq`), not by group.
- **Caveat.** West reads an imported manifest from the project's `manifest-rev` ref, which
  `west update` creates. An import is enabled only after the repository is pushed and has
  been updated once (`west update -k <project>` keeps the current branch).

## 14. Tool-Neutral Agent Setup

The platform supports all common AI coding tools (Claude Code, Codex, OpenCode,
Antigravity, Gemini CLI, Cursor, ...).

- **Canonical, committed:** `AGENTS.md` in every repository holds the rules, and skills follow the Agent Skills
  open standard in `platform/.agents/skills/<skill>/SKILL.md` (prefix `muon-`).
  `platform/.claude/skills` is a committed symlink to `../.agents/skills`.
- **Generated, never hand-edited, git-ignored in projects** (`west agents-sync`):
  - `CLAUDE.md` and `GEMINI.md` shims that import `@AGENTS.md`;
  - a workspace-root `AGENTS.md` (hub rules plus catalog);
  - per-skill links `.agents/skills/muon-*` and `.claude/skills/muon-*` at the workspace root
    **and in every project**, because Codex scans skills only up to the git root and Claude Code
    reads only `.claude/skills`;
  - per-tool permission adapters (§15, L3).

| Tool | Rules | Skills scanned |
|---|---|---|
| Codex | `AGENTS.md` (cwd up to git root) | `.agents/skills` (cwd up to git root) |
| OpenCode | `AGENTS.md` (`CLAUDE.md` fallback) | `.opencode/skills`, `.claude/skills`, `.agents/skills` |
| Antigravity | `AGENTS.md`, `GEMINI.md`, `.agents/rules` | `.agents/skills` |
| Claude Code | `CLAUDE.md` (imports `@AGENTS.md`; parent dirs too) | `.claude/skills` |
| Gemini CLI | `GEMINI.md` (imports `@AGENTS.md`) | `.gemini/skills`, `.agents/skills` |

Adding a tool means adding a shim or adapter in `scripts/west_commands/muon_ws/agents.py`. Canonical sources do not change.

## 15. Legacy Guardrails

Legacy protection does not depend on any single AI tool, and it works in every workspace
shape (full or repo-rooted).

| Layer | Mechanism | Applies to |
|---|---|---|
| L1 enforced | working tree read-only on disk (`.git` excluded); push URL disabled on every remote, submodules included; local `pre-commit`/`pre-push` hooks that refuse | every tool and every human |
| L2 instruction | each repository's `AGENTS.md` lists its legacy paths as read-only references | every tool that reads rules files |
| L3 ergonomics | generated tool-native settings that grant read access to `../legacy/*` and deny writes (Claude: `.claude/settings.local.json`; Codex: not needed, its sandbox keeps paths outside the repo read-only; others: adapter slots) | individual tools |

Archive trees in `archive/` (host-local, not in any manifest; see `legacy_inventory.md`) are
covered by L2 only. West has no local-only project type, and the commands work from manifests.

Legacy references are fetched and updated **only** with `west legacy sync`,
which clones or updates them and then re-applies L1. A bare `west update` of a legacy project is
not used. Legacy code that must run (golden-data generation) is built out of tree in
`<topdir>/.legacy-build/<dir>` (`west legacy build-dir <name>`).
