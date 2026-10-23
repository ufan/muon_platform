# ADR-012 Repository Baseline, Workspace Tooling and Workflow

Version: 1.0
Status: Accepted (2026-10-23)
Supersedes: ADR-009 §1, §2 (options), §3, §4, §6, §7, §8, §9, §10, §12, §13 (§5, §11, §14, §15 remain in force, adapted below)
Related: ADR-003 (service architecture), ADR-004 (versions), ADR-009, ADR-010, ADR-011
Change record: `changes/2026-10-workspace-reorg/`

## 1. Decision Summary

- **Every technical domain has its own repository.** `muon_core` is the scientific domain and is
  one domain among several. An upper **instrument** layer coordinates the domains.
- **Dependencies point one way.** Domains depend on system contracts only. Nothing depends on
  `muon_core` except instruments and offline consumers.
- **The workspace is a plain directory** composed from vcs2l `.repos` files in `platform/repos/`.
  All muon-specific workflow lives in one standalone CLI, `muon` (`platform/tools/muon`). West is no
  longer the workspace interface. A repository may still use west, or anything else, internally.
- **Rigor is staged.** During early prototyping (one developer, heavy use of AI agents) only the
  cheap, irreversible-loss-preventing rules apply. Further mechanisms are added when a named
  trigger fires (§6).
- **Workflow state lives in git**, so sessions, AI tools and hosts share one workflow (§8).

## 2. Context

On 2026-10-21/22 the workspace was organized around west (ADR-009): a hub that imports
repository manifests, about 1,000 lines of west extensions, and about 28 KB of agent rules loaded per DAQ session.
Two findings on 2026-10-23 changed this:

1. **The hardware domains have separate lifecycles.** Sensor subsystems (HV, gas, environment,
   pose, LV) are developed separately from the detector. A central controller integrates them.
   The detector domain is special: it produces what customers want, and it consumes other domains'
   data without coordinating them. Making it the hub would couple everything to it. So
   coordination belongs to a separate instrument layer, as in spacecraft bus/payload, observatory
   control systems (e.g. Rubin CSCs + ScriptQueue) and ISA-88 supervisory control.
2. **Development style.** There is one developer who relies heavily on AI agents across tools and
   hosts, and the project is at the scaffolding stage. Process must be cheap now and hardenable later.

West was also being used outside its design (locking, agent files, verification, test data,
branch workflows), and its model (manifest-rev, detached HEADs, import restrictions) produced
workarounds. Its native job, fetching and pinning repositories, is done equally well by vcs2l
(the maintained vcstool fork, `ros-infrastructure/vcs2l`). vcs2l keeps no workspace state.

## 3. Repository Baseline

| Repository | Responsibility |
|---|---|
| `muon_core` (`core/`) | Scientific domain: DAQ, scientific contracts (`contracts/science`), conditions interpretation, preprocess, reconstruction, reusable online/offline runners. Online and offline use the same library targets. |
| Domain repositories (future: HV, gas, env, pose, LV, …) | One per independently developed subsystem: firmware + domain service + simulator/fake + tests. Created when the domain's iteration starts (ADR-010). |
| `muon_instrument` (future; per product later) | Instrument coordination: orchestration and the instrument state machine, sequencing, interlock policy, aggregation/API gateway, CLI, product profiles, operational config, integration validation. Its release `.repos` file is the product bill of materials. Starts as one repository with `products/<name>/`. |
| `muon_contracts` (`contracts/`) | System contracts: the domain-service pattern, telemetry signal catalog, time base, conditions interchange, product-profile schema. A **placeholder** until the extraction trigger (§6). Until then the drafts live in `core/contracts/system/`. |
| `muon_platform` (`platform/`) | System requirements, architecture, decisions, guides, change records, the workspace definition (`repos/`), the `muon` tool and agent skills. No product code. |
| `muon_config` (`config/`) | Static detector/site parameter payloads (channel mapping, topology, geometry, alignment). Versions are append-only; schemas and interpretation live in core. Telemetry-derived conditions and operational config do not belong here. |
| `muon_testdata` (`testdata/`) | Versioned validation datasets and their tool (ADR-011). |
| Support repositories | `study`, `tools/*`: modified only on explicit request. |
| Legacy references | `legacy/<dir>`: read-only and locked (ADR-009 §5, §15). Host-local trees live in `archive/<dir>`. |

Planned outside core: detector front-end firmware (`muon_detector_fw`), simulation (`muon_sim`),
offline applications (imaging/density, data platform, digital twin). Each consumes core packages
and contracts and never copies their sources.

**Split test for leaving a repository** (replaces ADR-009 §4): split when the toolchain, lifecycle
or audience/ownership differs. A different deployment target alone is a packaging concern.

## 4. Dependency Rules

```text
muon_contracts (system)  <- everyone; depends on nothing
domain repos             -> system contracts only (never on each other, never on core)
muon_core                -> system contracts; sensor data only via telemetry/conditions contracts
muon_instrument          -> system contracts + domain and core service APIs (generated clients)
offline applications     -> core packages + contracts
muon_config              -> core schemas (validation only)
muon_platform            -> nothing at build time
```

**Control vs. data.** The instrument commands every domain, core included. Core never commands
another domain. Core may consume other domains' data, but only as conditions (§9).

## 5. Workspace Tooling

- **Composition:**
  - `platform/repos/workspace.repos` lists active and support repositories, including `platform` itself;
  - `platform/repos/legacy.repos` lists managed legacy references;
  - an optional, uncommitted `<topdir>/local.repos` holds per-host overrides.

  The files use the vcs2l format. Muon metadata goes in an optional `muon:` block, which vcs2l ignores.
- **Repository metadata:** `<repo>/.muon/repo.yml` (maturity, role, spec, verify, informs). It
  overrides the `muon:` block and travels with the repository.
- **`muon` CLI:**

  | Command | Purpose |
  |---|---|
  | `ws init` / `ws sync [--update] [--legacy]` | clone missing repos (vcs2l); fast-forward only clean repos on their pinned branch; legacy lock |
  | `status` | cross-repo branch, dirty, ahead/behind, pin drift, legacy lock state |
  | `verify [repo…]` | run the repos' verify commands |
  | `branch <name> <repo…>` | the same branch in several repos |
  | `freeze` | exact SHAs in vcs2l format (snapshot or BOM) |
  | `doctor` | tools, clones, locks, agent files, golden data root, rule-size limits |
  | `list`, `legacy list/status/build-dir` | listings |
  | `agents sync [--check]` | agent files (§8) |
  | `testdata …` | passes through to `testdata/tools/testdata.py` |

- **Independence:** no repository needs `muon`, vcs2l or west to build or test. Each verify
  command is a plain shell command run from the repository root.
- **Internal tooling is the domain's choice.** A domain may use west internally (e.g. Zephyr
  firmware with its modules), Conan, pixi, etc. The muon level does not depend on that choice.

## 6. Staged Rigor

**Always (cheap, and they prevent irreversible loss):**
- legacy references are read-only and locked;
- golden test data is immutable, and new data means a new version;
- config payloads are append-only versions;
- raw data is immutable;
- `verify` passes before push;
- never push, create remotes or delete branches without the owner's confirmation.

**Now (prototyping):**
- The prototype lane (ADR-010 §8) is the default. A change proposal is optional: write one to record a
  decision or to promote a prototype into the spec baseline.
- Agents may edit any repository in the workspace. Three rules apply:
  - **announce** every repository touched outside the one the session started in;
  - use the **same branch name** across repositories (`muon branch`);
  - **no silent pins**: run `muon status` before push.
- Contracts used only by core live in core, in the same commit as their consumer.
- One CI job per code repository runs its verify command.

**Hardening triggers:**

| Trigger | Add |
|---|---|
| Second domain or first instrument starts | Extract `core/contracts/system/` into `muon_contracts` (history kept); pin it by tag; `buf breaking` / schema-diff in its CI; a domain's `main` pins only tags |
| First instrument release or field deployment | Instrument `bom.repos` (`muon freeze`) as release identity; provenance enforced in data products |
| A contract has been stable for a while | Maturity `stable`; semver; breaking changes need an ADR |
| A second developer or an external hardware team | CODEOWNERS; per-domain `consumes:` declarations, a consumer index and reverse-dependency CI in `muon_contracts`; the `muon-propose-upstream` skill; change classes (below) become mandatory |
| Several domains change in parallel | Domain-rooted workspaces (a domain repo carries its own `.repos` that imports `platform/repos` fragments) |
| Second development host needs replay data | Remote store for golden bytes (ADR-011 amendment) |

**Change classes for upper layers** (mandatory once the second-developer trigger fires):

| Class | Example | From a domain context | Gate |
|---|---|---|---|
| D0 data | new alignment or dataset version | yes | the data repo's own validation |
| C0 own namespace, additive | new optional field in `domains/<d>/` | yes, as a PR | compatibility check + reverse-dependency CI green |
| C1 own namespace, breaking | rename a field in its own API | draft only | affected owners acknowledge; semver major |
| C2 `common/` or system spec | lifecycle FSM, requirement, ADR | draft only | change proposal; decided in the upper repo's context |

## 7. Agent Rules and Guides

- The root `platform/AGENTS.md` stays at or below about 3.5 KB, and each repository's `AGENTS.md` at or
  below about 2.5 KB (checked by `muon doctor`). These files hold the mission, map, hard rules and session
  protocol. Everything else goes into skills or docs that load on demand.
- Each procedure exists once, as a skill (`platform/.agents/skills/muon-*`, Agent Skills format).
  The human guide (`docs/workflow/DEVELOPER_GUIDE.md`) links to the skills instead of repeating them.
- Tool-neutral setup per ADR-009 §14: canonical `AGENTS.md` + skills, and generated shims, skill links and
  permission adapters (`muon agents sync`).

## 8. Continuity Across Sessions, Tools and Hosts

| State | Home |
|---|---|
| Rules, procedures | `AGENTS.md`, skills (git) |
| Decisions | ADRs; `docs/decisions.md` (dated one-line log for small decisions) |
| Work in progress | the active iteration's `changes/<iteration>/tasks.md` `## Next` section; pushed `wip/<topic>` branches |
| Workspace composition | `platform/repos/*.repos`, `.muon/repo.yml`; `muon freeze` snapshots |
| Environment | DEVELOPER_GUIDE toolchain section; `muon doctor` |
| Host-local data | `testdata/golden` (or `$MUON_DATA_ROOT`), `archive/`; listed by `muon doctor` |

**Session protocol** (skill `muon-session`):
- **start:** read the active `tasks.md` `## Next`, then run `muon status`;
- **end:** update `## Next`, commit, push the WIP branch (pushing needs the owner's confirmation).

**Tool memory** (e.g. assistant memory files) is a cache only. Anything that matters for the next
session or another tool goes into the repository.

## 9. Data Planes, Time and Conditions

- **Three planes:**
  - control: commands, state, alarms;
  - scientific data: raw → EDM → products, run-scoped, immutable raw;
  - sensor/telemetry: low-rate continuous time series, stored locally first and then forwarded.
- **Telemetry reaches reconstruction only as conditions.**
  - Online, a live provider supplies the current values and records every value it hands out.
  - Offline, a conditions builder derives versioned payloads with validity intervals from the
    archive: gas state and gain factors, HV good-time intervals, pose segments.
  - Algorithms never query telemetry directly.
- **Conditions have two kinds of sources:**
  - static tiers: detector model in core; instrument assembly and deployment geometry/alignment in `config`;
  - dynamic, telemetry-derived intervals.

  Both resolve into an immutable snapshot with an ID and content hash.
- **Time base:**
  - the edge appliance clock is the only common reference (it keeps both monotonic + `boot_id` and UTC);
  - sensor controllers and the DAQ electronics have no shared clock; each source is mapped to edge
    time through clock-correlation records, with a recorded uncertainty;
  - the accuracy budget is about 1 s, so no PTP is needed;
  - the raw capture records `boot_id`, the clock sync state and periodic clock-correlation records.

  These contracts are staged in `core/contracts/system/`.

## 10. Provenance

- A software state is identified by the core SHA or tag. The full workspace state is `muon freeze`
  output, and later the instrument's BOM.
- Every scientific product records the core SHA, the conditions snapshot ID + hash, the firmware
  version and the instrument version (ADR-004 §7).

## 11. Consequences

Positive:
- low friction now: one workspace, no proposals for prototypes, short rules;
- hardening steps are written down and reversible;
- no workspace-tool state;
- domains follow real lifecycle boundaries.

Negative and mitigations:
- **No atomic commits across repositories.** Mitigated by keeping co-evolving code in core and by the same-branch rule.
- **Contract drift is possible once domains multiply.** Mitigated by the triggers in §6.
- **Rule compliance depends on agents reading `AGENTS.md`.** Mitigated by the legacy L1 lock, `muon doctor`, CI, and fresh-session checks.

## 12. Validation

- `muon` unit tests (`platform/tools/muon/tests`).
- `muon doctor` is clean in the workspace.
- `muon verify` passes for every repository with a verify command.
- A fresh agent session in `core/` (with at least two different AI tools) follows the session
  protocol and verifies before finishing.
