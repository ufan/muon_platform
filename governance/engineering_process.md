# Engineering process

Status: current. The project-management rules in force: how the product is developed, specified,
changed and hardened. Procedures are in the [developer guide](developer_guide.md) and the skills
(`.agents/skills/`); session scope is in [work discovery](../work/README.md). Consolidated
2026-10-26 from the retired workflow ADRs 009, 010, 012 and 013 (full text in git).

## 1. Development approach

- **Bottom-up, one domain at a time**, from the coarse map in
  [scientific data path](../docs/architecture/system_architecture.md#5-scientific-data-path). Order of the scientific chain:
  DAQ → preprocess → recon → imaging/analysis. Hardware domains start when their iteration starts.
- **Strangler fig:** each new domain replaces its legacy stage while the chain keeps working.
- **Domain iteration playbook** (skill `muon-domain-iteration`): scope → legacy archaeology →
  golden data → to-be spec and contracts (baseline, §4) → skeleton and failing tests → implement → differential
  verification → strangler switch → retire legacy. Steps are tracked per capability. Every agent
  choice in an iteration has an autonomy class: `ship` (agent proceeds), `show` (agent proceeds on a
  provisional decision request that an approver settles later) or `ask` (wait for the owner). Only `ask` blocks: hard stops, the other
  `ask` classes (new iterations, requirements, ADRs, governance, breaking contracts, controlled specs)
  and the escalation triggers in the skill.
- **Port, refactor or rewrite** is decided per domain at the to-be spec step:
  - refactor in place: the code is sound and in the right language and runtime; only the structure is wrong;
  - port: the logic is valuable, the language, runtime or structure is not; import history so
    provenance survives;
  - rewrite from spec: legacy is only a behaviour reference and a golden-data source (DAQ, 2026-10).

## 2. Specification levels

The project is specified at two levels that follow the same process. Platform is the **system
level**: what the instrument is and how its parts fit. Each **component repository** (repository
model) specifies and develops its part in detail.

| Layer | System level (`platform`) | Component level (each component repository) |
|---|---|---|
| Requirement | `docs/requirements/` (`SYS-NNN`, `HV-NNN`, …) | its own requirements (`FR-NNN`; `daq:FR-001` outside it) |
| Architecture, decision | `docs/architecture/`, `docs/adr/` | its own architecture and ADRs (`daq:ADR-006`) |
| Behaviour spec | — | `openspec/specs/<capability>/`: SHALL requirements with scenarios |
| Component spec | — | design, rationale and interpretation rules, linked from `SPEC.md` |
| Contract | interface rules (ADR-003, ADR-014) | machine-readable: protobuf, schemas, state-machine tables (`core/contracts/`; device wire protocol in `core/daq/ref/<target>/`) |
| Verification | system and integration tests (instrument, later) | unit, contract, conformance, golden-data and replay tests |
| Plan | iterations (`iterations/`) | its own roadmap, if any |

- **Flow-down:** system requirements, architecture and ADRs constrain every component. A component
  requirement cites the system requirement or ADR it refines, where one exists.
- **Encapsulation:** a component's own requirements, architecture, ADRs and specs are internal.
  Other repositories rely only on its contracts and on the specs it publishes for them, cited with
  the repository qualifier (`core:domain-service`).
- **Flow-up:** a component that finds a system requirement or decision wrong or missing raises it at
  the system level (requirement change or ADR); it never diverges silently.
- **Shared system behaviour** is specified where its contract lives: in core next to
  `core/contracts/system/` now, in `contracts` after extraction (§5).
- **One fact, one home.** The requirement file states the need (one line and its acceptance); the
  behaviour spec states the observable behaviour and cites the requirement, never copying it; the
  component spec explains design and rationale and links the behaviour spec and contract instead of
  repeating them.
- Each layer should end in something a program can check. Tests name the requirement or spec IDs they cover.

## 3. Requirement IDs

- Repositories own their requirement IDs (e.g. `FR-001` in `core/daq/doc/feature-requirements.md`);
  outside the owner, qualify them: `daq:FR-001`. Repository decision records are qualified the same
  way (`daq:ADR-006`).
- Platform requirements use `<AREA>-<NNN>` (`SYS-001`, `HV-001`), assigned when a domain enters its iteration.
- IDs are never reused or renumbered; retired IDs are marked as removed.

## 4. Changes

### Terms

| Term | Meaning |
|---|---|
| Decision | a settled choice, approved by someone with the authority; lives in an ADR, a spec or the decision log. Only decisions are authoritative |
| Decision request | an iteration item asking for a decision (`open → provisional → approved / rejected`); approved, it becomes a decision and is restated in its home document |
| Approval | the act that settles a request or an OpenSpec change, recorded with approver, kind, date and authority (§7) |
| Autonomy class | how far an agent may go alone: `ship`, `show`, `ask` (skill `muon-domain-iteration`) |
| Change class | ownership and compatibility of an upper-layer change, D0/C0/C1/C2 (§5); C1 and C2 are at least `ask`, D0 and C0 at least `show` |

### Stages of a capability

A capability is a cohesive unit of observable behaviour (the DAQ device state machine, the
domain-service contract, the raw capture format). Each one passes through three stages:

| Stage | When | Rule |
|---|---|---|
| Exploration | before its first approved spec | Prototype to expose the real needs (branches, spikes, `/opsx:explore`); no gate. Output: findings and candidate requirements. |
| Baseline | iteration step 3 of its domain (§1) | The first OpenSpec change of the capability creates its spec from what was learned; the owner approves it. |
| Controlled | after the baseline | Every behaviour change goes through an approved OpenSpec change. An experiment stays on a throwaway branch and merges only through a change. |

The stage is mechanical: a capability is controlled once `openspec/specs/<capability>/` exists in
its repository. Repository maturity (§6) summarises the stages of its capabilities.

### Behaviour changes

A behaviour change is one that a client, operator, another component, a data consumer or a
black-box test can observe through a defined interface:

- control behaviour: states, command acceptance and results, recovery;
- fault and safety handling: health, alarms, interlock reactions, timeouts;
- contracts and data formats: messages, fields, record and file layouts, APIs used by another repository;
- data products and scientific results, including any change in numerical output;
- configuration meaning: new parameters, defaults, units;
- performance guarantees the spec states.

Not behaviour changes: refactoring, internal APIs used only inside the repository, speed-ups that
change no stated guarantee, build and tooling, tests of specified behaviour, documentation, and
fixes that restore the specified behaviour. A fix where the spec is silent decides behaviour: it is
a change, and it adds the missing rule.

### OpenSpec changes (component level)

1. **Propose** (`/opsx:propose <name>`): proposal (why, what, impact, the iteration task it serves,
   `## Approval` with `Status: pending`); spec delta whose requirements cite the requirement IDs they
   refine; design when there is a real choice (sources compared with their authority, alternatives);
   tasks ending in a `## Verification` group (exact commands, hardware tests not run). Commit it.
2. **Approve:** only the owner sets `Status: approved` with name and date, or an agent does so on
   the owner's instruction and quotes it in the commit, or an agent approver within a delegation the
   owner recorded (§7).
3. **Apply** (`/opsx:apply`, any AI tool): implement, name tests after requirement IDs, run
   `muon verify <repo>`, commit. A baseline change (the capability is not yet controlled) may be
   applied on its task branch before approval; a change to a controlled capability waits for
   approval. Specs are not merged during apply.
4. **Archive** (`/opsx:archive`): only after approval. Merge the spec delta into `openspec/specs/`,
   move the change to `openspec/changes/archive/`, commit; then update the iteration task. Nothing
   that depends on an unapproved change merges to `main`.

Work spanning repositories is one change per repository, linked from the iteration task. A change
that depends on another names it (`Depends on: <repo>/<change>`) and is archived after it.
Configuration: `openspec/config.yaml` from `templates/project/openspec/`, without a forked
OpenSpec workflow; generated per-tool OpenSpec files are git-ignored and rebuilt by `openspec update`.

### System-level changes (platform)

- **Iterations** (`iterations/`, skill `muon-domain-iteration`) plan and order work across
  repositories; their tasks link the component changes that carry them out.
- Requirements, architecture and governance change by commits the owner approves. Notes (`docs/notes/`) are
  promoted with skill `muon-promote`.

### Rules for every change

- Contracts used only by core change in the same commit as their consumer.
- **Agents draft; the owner approves** requirements, ADRs, behaviour changes and their baselines, and
  merges to platform docs. An agent approver may settle only the classes of decision request the owner
  has delegated (§7).
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
  [decision_log.md](decision_log.md) if they pass its admission test.
- **Landing.** A product decision is authoritative only in its home: the requirement, architecture,
  ADR, component spec, contract or OpenSpec change it belongs to. A decision log entry or an approved
  decision request names that home and is restated there, citing the record (`landed`). Landing an
  approved decision is `ship` unless it changes a requirement (`ask`). It happens at the latest when the
  capability is baselined (iteration step 3), before work that depends on it merges to `main`, and
  at the end of the iteration. The integrator lands, using skill `muon-promote`.

## 5. Staged rigor

**Always** (cheap; they prevent irreversible loss):

- legacy references are read-only and locked; golden test data, raw data and config payloads are
  immutable (new data means a new version);
- `muon verify` passes before push;
- never push, create remotes or delete branches without the owner's confirmation.

**Now** (one developer, heavy AI use, prototyping):

- agents may edit any repository; they announce every repository touched outside the starting one,
  use the same branch name across repositories (`muon branch`) and run `muon status` before push;
- one CI job per code repository runs its verify command;
- work is non-blocking by default: agents proceed on `show` decision requests, recorded as
  provisional, and the owner settles them in one pass when work merges. Only `ask` waits: irreversible
  actions, the other `ask` classes and the escalation triggers (skill `muon-domain-iteration`).

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

When a trigger fires, add the mechanism and record it in `decision_log.md`.

**Change classes for upper layers** (mandatory from the second-developer trigger):

| Class | Example | From a domain context | Gate |
|---|---|---|---|
| D0 data | new alignment or dataset version | yes | the data repository's validation |
| C0 own namespace, additive | new optional field | yes, as a PR | compatibility check and reverse-dependency CI |
| C1 own namespace, breaking | rename a field in its own API | draft only | affected owners acknowledge; semver major |
| C2 shared or system spec | lifecycle state machine, requirement, ADR | draft only | OpenSpec change in the repository that owns the shared spec, with consumers named in the proposal; requirement or ADR change at the system level |

## 6. Repositories and workspace

- Repository boundaries and dependencies: [ADR-015](../docs/adr/ADR-015_repository_and_instrument_layering.md),
  [repository model](../docs/architecture/repository_model.md). Adding one: skill `muon-new-project`.
- **Maturity** (`.muon/repo.yml`):

  | Level | Meaning | Rules |
  |---|---|---|
  | `legacy` | old implementation, reference only | read-only and locked; never a dependency |
  | `support` | data or tools off the production path (study, tools, test data) | change only on explicit request |
  | `incubating` | new; contracts provisional | capabilities mostly in exploration (§4); breaking changes allowed |
  | `active` | domain in its iteration | baselined capabilities under change control (§4); full verification |
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
  | Decisions | ADRs; `governance/decision_log.md` (at most about 30 active entries) |
  | Work discovery, plans | `work/index.yml`; iteration records (`iterations/`) |
  | Behaviour specs and changes | each component repository's `openspec/` |
  | Scoped work in progress | explicit assignment and its handoff; isolated branches or worktrees |
  | Workspace composition | `platform/repos/*.repos`, `.muon/repo.yml`; `muon freeze` snapshots |
  | Host-local data | `testdata/golden` or `$MUON_DATA_ROOT`, `archive/` |

- Tool memory is a cache only.
- **Work discovery** ([work/README.md](../work/README.md), skill `muon-session`): an explicit
  assignment comes first; the work index is orientation, not a queue, lock or approval, and may list
  several active iterations. Unassigned unattended sessions stop. Concurrent writers use isolated
  checkouts, and a designated integrator maintains shared iteration summaries. Evaluate existing
  coordination tools before building claims, leases or scheduling.

### Agent roles

Roles are responsibilities and authority, not identities. In solo work, one session (or the owner)
may hold several roles. With multiple agents, each assignment names its role (`work/README.md`).

| Role | Does | Decides | Never |
|---|---|---|---|
| Owner (human) | sets scope and the delegation policy | `ask` requests; hard stops; governance; the delegation policy | — |
| Coordinator | splits an iteration into bounded, non-overlapping assignments; tracks blockers | which worker gets which assignment | approves; implements |
| Worker | implements one assignment (a capability or feature) in an isolated worktree | `ship` choices; proposes `show` requests in its handoff | edits shared iteration summaries; reviews its own work |
| Reviewer | independent readiness, citation and consistency checks; golden comparison reports | whether work is ready; `show` approvals only where delegated | reviews work it authored |
| Integrator | integrates worker results on the task branch; keeps the decision requests, `## Revisions` and `## Next`; prepares merges | how results are integrated | approves its own merge |
| Documentation (optional) | keeps indexes, `context.md` and cross-links consistent | wording and structure | changes behaviour content (one fact, one home) |

- **Approver** is a role the delegation policy binds. Today it is the owner. An iteration's
  `## Delegation` may grant classes of `show` requests to an agent approver, with conditions.
- **Separation of duties:** author, reviewer and approver of one artifact are different sessions, and
  preferably different tools or models. In solo work the owner is the approver, and the author and
  reviewer are still separate agent sessions. A directed session without a named integrator is its own
  integrator.
- **Never delegated:** hard stops (push, merge to `main`, spec archive, golden-data import, strangler
  switch, retire), new iterations, requirements, ADRs, governance and the delegation policy itself.
- **Approval record:** `Status: approved — <approver>, human|agent:<tool/model>, <date>, authority: owner|delegation <id>`.
