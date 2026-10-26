# Engineering process

Status: current. The project-management rules in force: how the product is developed, specified,
changed and hardened. Procedures are in the [developer guide](developer_guide.md) and the skills
(`.agents/skills/`); session scope is in [work discovery](../work/README.md). Consolidated
2026-10-26 from the retired workflow ADRs 009, 010, 012 and 013 (full text in git).

## 1. Development approach

- **Bottom-up, one domain at a time**, from the coarse map in
  [architecture overview](../docs/architecture/architecture_overview.md). Order of the scientific chain:
  DAQ → preprocess → recon → imaging/analysis. Hardware domains start when their iteration starts.
- **Strangler fig:** each new domain replaces its legacy stage while the chain keeps working.
- **Domain iteration playbook** (skill `muon-domain-iteration`): scope → legacy archaeology →
  golden data → to-be spec and contracts → skeleton and failing tests → implement → differential
  verification → strangler switch → retire legacy.
- **Port, refactor or rewrite** is decided per domain at the to-be spec step:
  - refactor in place: the code is sound and in the right language and runtime; only the structure is wrong;
  - port: the logic is valuable, the language, runtime or structure is not; import history so
    provenance survives;
  - rewrite from spec: legacy is only a behaviour reference and a golden-data source (DAQ, 2026-10).

## 2. Specification layers

Each layer should end in something a program can check. Tests name the requirement or spec IDs they cover.

| Layer | Location | Form |
|---|---|---|
| Requirement | `platform/docs/requirements/`, `<repo>/…/feature-requirements.md` | prose with stable IDs (§3) |
| Architecture, decision | `platform/docs/architecture/`, `platform/docs/adr/` | prose |
| Component spec | `<repo>/SPEC.md` and what it links | behaviour and acceptance criteria referencing requirement IDs |
| Contract | `core/contracts/` (science; system until extraction), `core/daq/ref/<target>/` (device ↔ host wire protocol) | machine-readable: schemas, protobuf, state-machine tables |
| Conformance, behaviour | `<repo>/tests/`, golden datasets | contract tests, golden-data and replay tests |

## 3. Requirement IDs

- Repositories own their requirement IDs (e.g. `FR-001` in `core/daq/doc/feature-requirements.md`);
  outside the owner, qualify them: `daq:FR-001`. Repository decision records are qualified the same
  way (`daq:ADR-006`).
- Platform requirements use `<AREA>-<NNN>` (`SYS-001`, `HV-001`), assigned when a domain enters its iteration.
- IDs are never reused or renumbered; retired IDs are marked as removed.

## 4. Changes

- **Prototype lane is the default.** Prototype freely inside a repository; its own `AGENTS.md` governs.
- A **change proposal** (`platform/changes/`, skill `muon-new-change`) is optional. Write one to record
  a decision or to promote prototype behaviour into the spec baseline (spec deltas with acceptance
  criteria). Design notes are promoted with skill `muon-promote`.
- Contracts used only by core change in the same commit as their consumer.
- **Agents draft; the owner approves** requirements, ADRs, contract changes and merges to platform docs.
- Definition of done: `muon verify` passes for changed repositories, specs and docs are updated,
  tests reference requirement IDs.
- **Agents commit their own work.** After `muon verify` passes, the agent that made a scoped change
  commits it in each changed repository, on the task branch, and only its own changes (never another
  session's). Committing is not publishing: pushing, merging to `main` and deleting branches still
  need the owner's confirmation.
- **Commit format** (all tools; not Conventional Commits, so no `feat(...)!:` types):
  - Subject `<scope>: <summary>`, at most 72 characters, no trailing period. The scope is the area
    changed: a module (`daq`), tool (`muon`), document area (`docs`, `governance`), file
    (`AGENTS.md`) or mechanism (`openspec`). The summary says what changes.
  - Body, unless trivial: why, wrapped at about 100 columns, citing requirement IDs, ADRs and the
    change or task. Contract changes say `additive` or `breaking`; a breaking interface change
    starts a body line with `BREAKING:`. An approval made on the owner's instruction quotes it.
  - Commits made by an AI tool end with `Co-Authored-By: <tool or model> <noreply address>`.
- Decisions: consequential choices with alternatives become ADRs; small ones go to
  [decisions.md](decisions.md) if they pass its admission test.

## 5. Staged rigor

**Always** (cheap; they prevent irreversible loss):

- legacy references are read-only and locked; golden test data, raw data and config payloads are
  immutable (new data means a new version);
- `muon verify` passes before push;
- never push, create remotes or delete branches without the owner's confirmation.

**Now** (one developer, heavy AI use, prototyping):

- agents may edit any repository; they announce every repository touched outside the starting one,
  use the same branch name across repositories (`muon branch`) and run `muon status` before push;
- one CI job per code repository runs its verify command.

**Hardening triggers:**

| Trigger | Add |
|---|---|
| Second domain or first instrument starts | Extract `core/contracts/system/` into `muon_contracts` with history; pin by tag; schema-breaking checks in its CI; a domain's `main` pins only tags |
| First instrument release or field deployment | Instrument bill of materials (`muon freeze`) as release identity; provenance enforced in data products |
| A contract stays stable | Maturity `stable`; semver; breaking changes need an ADR |
| Second developer or an external hardware team | CODEOWNERS; per-domain `consumes:` declarations with reverse-dependency CI; the change classes below become mandatory |
| Several domains change in parallel | Domain-rooted workspaces (a domain repository carries a `.repos` that imports platform fragments) |
| Shared behaviour specs owned apart from their consumers (second developer, external team, or several domains in parallel) | Evaluate an OpenSpec store (e.g. `contracts`) that component repositories reference read-only |
| Second development host needs replay data routinely | Remote store for golden bytes ([ADR-011](../docs/adr/ADR-011_test_data.md)) |

When a trigger fires, add the mechanism and record it in `decisions.md`.

**Change classes for upper layers** (mandatory from the second-developer trigger):

| Class | Example | From a domain context | Gate |
|---|---|---|---|
| D0 data | new alignment or dataset version | yes | the data repository's validation |
| C0 own namespace, additive | new optional field | yes, as a PR | compatibility check and reverse-dependency CI |
| C1 own namespace, breaking | rename a field in its own API | draft only | affected owners acknowledge; semver major |
| C2 shared or system spec | lifecycle state machine, requirement, ADR | draft only | change proposal, decided in the upper repository |

## 6. Repositories and workspace

- Repository boundaries and dependencies: [ADR-015](../docs/adr/ADR-015_repository_and_instrument_layering.md),
  [repository model](../docs/architecture/repository_model.md). Adding one: skill `muon-new-project`.
- **Maturity** (`.muon/repo.yml`):

  | Level | Meaning | Rules |
  |---|---|---|
  | `legacy` | old implementation, reference only | read-only and locked; never a dependency |
  | `support` | data or tools off the production path (study, tools, test data) | change only on explicit request |
  | `incubating` | new; contracts provisional | prototype lane; breaking changes allowed |
  | `active` | domain in its iteration | spec-driven, full verification |
  | `stable` | contracts frozen, semver | breaking changes need an ADR |

- **Workspace:** a plain directory composed from vcs2l `.repos` files in `platform/repos/`; all
  muon workflow lives in the `muon` tool. No repository needs `muon`, vcs2l or west to build or
  test; a domain chooses its internal tooling (west for Zephyr, Conan, pixi, …).
- GitHub is the default remote; legacy and support repositories may keep others.
- **Legacy:** managed references live in `legacy/<dir>` (locked on disk, pushes disabled, refusing
  hooks; listed in `platform/repos/legacy.repos`); host-local trees without a remote live in
  `archive/<dir>` and are protected by the rules only. Both are recorded in the
  [legacy inventory](../docs/legacy_inventory.md). Never a build or runtime dependency; build out of
  tree. Knowledge from legacy code goes into the as-is spec; copied code records its source
  (repository, path, commit).

## 7. Agents and continuity

- `platform/AGENTS.md` stays at or below about 3.5 KB and each repository's `AGENTS.md` at or below
  about 2.5 KB (`muon doctor`). They hold the mission, map, hard rules and session protocol; details
  load on demand from `context.md`, docs and skills. Each procedure exists once, as a skill.
- Rules are tool-neutral: canonical `AGENTS.md` and skills; `muon agents sync` generates the
  per-tool shims, skill links and permission adapters.
- State lives in git so sessions, tools and hosts share one workflow:

  | State | Home |
  |---|---|
  | Rules, procedures | `AGENTS.md`, skills |
  | Decisions | ADRs; `governance/decisions.md` (at most about 30 active entries) |
  | Work discovery, plans | `work/index.yml`; linked proposal and task records |
  | Scoped work in progress | explicit assignment and its handoff; isolated branches or worktrees |
  | Workspace composition | `platform/repos/*.repos`, `.muon/repo.yml`; `muon freeze` snapshots |
  | Host-local data | `testdata/golden` or `$MUON_DATA_ROOT`, `archive/` |

- Tool memory is a cache only.
- **Work discovery** ([work/README.md](../work/README.md), skill `muon-session`): an explicit
  assignment comes first; the work index is orientation, not a queue, lock or approval, and may list
  several active iterations. Unassigned unattended sessions stop. Concurrent writers use isolated
  checkouts, and a designated integrator maintains shared iteration summaries. Evaluate existing
  coordination tools before building claims, leases or scheduling.
