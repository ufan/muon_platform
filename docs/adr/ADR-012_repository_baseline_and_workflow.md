# ADR-012 Repository baseline, workspace tooling and workflow

Status: Accepted (2026-10-23; re-baselined 2026-10-25, absorbing the parts of ADR-009 still in force)
Change record: `changes/archive/2026-10-workspace-reorg/`

## 1. Decision summary

- Every technical domain has its own repository; `muon_core` is the scientific domain. An
  instrument layer coordinates the domains.
- Dependencies point one way: domains depend only on system contracts.
- The workspace is a plain directory composed from vcs2l `.repos` files; the `muon` CLI holds all
  workspace workflow.
- Rigor is staged: cheap loss-preventing rules now, more when a named trigger fires (§6).
- Workflow state lives in git, shared by all sessions, AI tools and hosts (§8).

## 2. Context

Sensor subsystems (HV, gas, LV, pose, environment) are developed separately from the detector, and
the detector domain consumes their data without coordinating them; coordination therefore belongs
to a separate instrument layer. One developer works with many AI tools and hosts at the
scaffolding stage, so process must be cheap now and hardenable later. West was replaced because
it was used far outside its design; vcs2l does its native job (fetch and pin) without state.

## 3. Repository baseline

Repositories and their responsibilities are in the [repository model](../architecture/repository_model.md).
Split a repository only when toolchain, lifecycle or audience differs.

## 4. Dependency rules

Domains depend on system contracts only; core receives sensor data only as conditions; the
instrument uses domain and core service APIs; offline applications use core packages; platform has
no build-time dependency. The instrument commands every domain, core included; core never commands
another domain.

## 5. Workspace tooling

- `platform/repos/workspace.repos` (active and support repositories) and `legacy.repos` (legacy
  references), in vcs2l format with an optional `muon:` block; optional uncommitted `local.repos`.
- `<repo>/.muon/repo.yml` holds maturity, role, spec, verify command and `informs`. Maturity:

  | Level | Meaning |
  |---|---|
  | `legacy` | old implementation; read-only reference |
  | `support` | data, studies, tools; changed only on explicit request |
  | `incubating` | new; contracts provisional |
  | `active` | in its domain iteration |
  | `stable` | contracts frozen; breaking changes need an ADR |

- `muon` commands: `ws init/sync`, `status`, `verify`, `branch`, `freeze`, `doctor`, `list`,
  `legacy …`, `agents sync`, `testdata …`. A global dependency-free launcher (`muon-workspace`)
  runs the implementation pinned by each workspace's platform checkout (`platform/tools/muon`, via uv).
- No repository needs `muon` to build or test; verify commands are plain shell commands. A domain
  may use any internal tooling (west, Conan, …).

## 6. Staged rigor

**Always:** legacy references read-only and locked; golden data, raw data and config payloads
immutable or append-only; `verify` passes before push; no push, remote creation or branch deletion
without the owner's confirmation.

**Now (prototyping):** prototyping is the default and change proposals are optional (ADR-010 §8).
Agents may edit any repository but announce repositories touched outside their starting one, use
the same branch name across repositories, and run `muon status` before push. Contracts used only
by core change in the same commit as their consumer. One CI job per repository runs its verify command.

**Hardening triggers:**

| Trigger | Add |
|---|---|
| Second domain or first instrument | extract `core/contracts/system/` to `muon_contracts`; tags, breaking-change checks |
| First instrument release or field deployment | instrument BOM (`muon freeze`); enforced product provenance |
| A contract stable for a while | maturity `stable`, semver, ADR for breaking changes |
| Second developer or external hardware team | CODEOWNERS, consumer index and reverse-dependency CI, mandatory change classes |
| Several domains change in parallel | domain-rooted workspaces |
| Second host needs replay data | remote store for golden bytes (ADR-011) |

## 7. Agent rules and setup

- `platform/AGENTS.md` ≤ about 3.5 KB and each repository's `AGENTS.md` ≤ about 2.5 KB (`muon
  doctor` checks): mission, map, hard rules, session protocol. Everything else is in skills or docs.
- Each procedure exists once, as a skill in `platform/.agents/skills/muon-*`; guides link to them.
- Canonical sources are `AGENTS.md` and the skills. `muon agents sync` generates, never by hand:
  `CLAUDE.md`/`GEMINI.md` shims, the workspace-root `AGENTS.md`, per-repository skill links and
  per-tool permission adapters. Adding an AI tool means adding a shim or adapter.

## 8. Continuity across sessions, tools and hosts

| State | Home |
|---|---|
| Rules, procedures | `AGENTS.md`, skills |
| Decisions | ADRs; `docs/decisions.md` for small decisions passing its log test (archived yearly; `muon doctor` warns above 30) |
| Work discovery | `work/index.yml` and linked iteration records ([ADR-013](ADR-013_work_discovery_and_session_scope.md)) |
| Workspace composition | `platform/repos/*.repos`, `.muon/repo.yml`, `muon freeze` |
| Host-local data | golden data root, `archive/` (reported by `muon doctor`) |

Tool memory is a cache; anything needed by another session or tool goes into a repository.

## 9. Data planes, time and conditions

Three planes (control, scientific data, telemetry); telemetry reaches algorithms only as
immutable conditions snapshots; the edge clock is the common time base with clock-correlation
records and a ~1 s budget. Details: [system architecture §4–§6](../architecture/system_architecture.md#4-information-planes).
Contracts are staged in `core/contracts/system/`.

## 10. Provenance

A software state is identified by the core SHA or tag, the full workspace by `muon freeze` and
later the instrument BOM. Every product records core SHA, conditions snapshot ID and hash, firmware
and instrument version.

## 11. Legacy guardrails

| Layer | Mechanism |
|---|---|
| L1 enforced | read-only working tree, disabled push URLs and refusing git hooks, applied by `muon ws sync --legacy` |
| L2 instruction | `AGENTS.md` lists legacy and archive paths as read-only |
| L3 tool settings | generated permission adapters grant read and deny write |

Legacy references live in `legacy/<dir>` (managed, in `legacy.repos`, with `informs`); host-local
trees without a remote live in `archive/<dir>` (L2 only). Legacy code runs only from out-of-tree
builds (`muon legacy build-dir`).

## 12. Validation

`muon` unit tests pass, `muon doctor` is clean, `muon verify` passes for every repository, and a
fresh session in each AI tool follows the session protocol.
