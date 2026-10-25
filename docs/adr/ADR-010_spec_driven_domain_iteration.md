# ADR-010 Spec-Driven Domain Iteration

Version: 1.0
Status: Accepted (2026-10-21); partly superseded by [ADR-012](ADR-012_repository_baseline_and_workflow.md) (§3, §5–§6: repository/contract placement, tooling, proposal/prototype rules in §2–§3 and §8)
Extends: ADR-006 §4 "Specification Driven Development"
Related: ADR-008 (replay), ADR-009 (workspace model)
Revised: 2026-10-21 (§8 prototype lane; §4 step 8); 2026-10-23 (ADR-012: prototype lane is the default, proposals optional, `muon verify`)

> **2026-10-23 (ADR-012 §6).** While the platform is in early prototyping with one developer, the
> prototype lane (§8) is the default for all work. A change proposal (§3) is written only to record a
> decision or to promote prototype behaviour into the spec baseline. Contracts used only by `core`
> change in the same commit as their consumer. `west verify` reads `muon verify`, and `west legacy sync`
> reads `muon ws sync --legacy`. Mandatory proposals return with the hardening triggers in ADR-012 §6.

## 1. Decision Summary

The platform is built **bottom-up, one domain at a time**, from a coarse
global landscape (`docs/architecture/architecture_overview.md`). Each domain goes through a
fixed **iteration playbook** that turns legacy code and domain knowledge
into executable specifications before any implementation. The system is
migrated with the **strangler-fig** pattern: new domains replace legacy
stages one by one while the chain keeps working.

Changes to specifications are made as **change proposals**: deltas against
the living specs, in the style of OpenSpec. AI agents implement against
approved proposals and verify against machine-checkable criteria.

Iteration order: **DAQ → preprocess → recon → imaging/analysis**.
Simulation and conditions run alongside when needed.

## 2. Specification Layers

Each layer should end in something a program can check:

| Layer | Location | Form |
|---|---|---|
| Requirement | `platform/docs/requirements/` | prose with stable IDs (§7) |
| Architecture / decision | `platform/docs/architecture/`, `platform/docs/adr/` | prose |
| Component spec | `<project>/SPEC.md` | behaviour and acceptance criteria referencing requirement IDs |
| Contract | `contracts/` (cross-repo); `daq/ref/<target>/` (device ↔ host wire protocol) | machine-readable: schemas, OpenAPI/AsyncAPI or protobuf, state-machine tables; ASN.1 for the wire protocol |
| Conformance | `<project>/tests/` | generated code, contract tests |
| Behaviour | `<project>/tests/`, replay datasets | golden-data and replay tests (ADR-008) |

Tests name the spec or requirement IDs they cover.

## 3. Change Lifecycle

> **Not the current procedure as written (ADR-012 §3, §6).** Proposals are optional while prototyping.
> Contracts used only by `core` change in the same commit as their consumer; shared system contracts
> are staged in `core/contracts/system/` ([repository model](../architecture/repository_model.md)), not `contracts/`.
> Cross-repository work follows the [developer guide §4](../workflow/developer_guide.md#4-cross-repository-changes), not ADR-009 §8.

Changes to `contracts/`, changes spanning several repositories, and promotions of prototype behaviour into the spec baseline follow this lifecycle (intra-repository work: see §8):

1. **Propose**: `platform/changes/<yyyy-mm>-<slug>/` with `proposal.md`
   (why, scope, affected projects), `specs.md` (deltas against living specs),
   `contracts.md` (contract diff or link), and `tasks.md`.
2. **Review**: a human approves. Agents may draft, but never approve,
   proposals, ADRs, or contract changes.
3. **Freeze contracts**: contract changes merge first in `contracts/`.
   After that, producers and consumers can be implemented in parallel.
4. **Implement**: tasks reference proposal and spec IDs. Cross-repo work follows
   ADR-009 §8.
5. **Verify**: `muon verify` for the affected repositories; contract, unit and golden tests.
6. **Archive**: deltas are merged into the living specs. The proposal moves to
   `changes/archive/`.

## 4. Domain Iteration Playbook

| Step | Output |
|---|---|
| 0. Scope | boundary of the domain in `architecture_overview.md`; "downstream needs" of its outputs |
| 1. Legacy archaeology | **as-is spec**: inputs, outputs, file formats, calibration dependencies, failure modes, implicit physics/hardware knowledge |
| 2. Golden data (ADR-011) | recorded inputs and legacy (or hardware) outputs with tolerances; where legacy cannot run, recorded hardware captures plus hand-checked expectations |
| 3. To-be spec and contracts | spec deltas, provisional contracts, ADRs for significant choices, and the **port / refactor / rewrite** decision |
| 4. Skeleton and failing tests | interfaces, contract tests, golden comparisons |
| 5. Implement | port, refactor or rewrite |
| 6. Differential verification | output matches legacy/golden data except for **documented, intentional deviations** |
| 7. Strangler switch | the new domain replaces legacy in the chain; its contracts are promoted |
| 8. Retire | the old repository is frozen (tag `legacy-final`), moved to `legacy/<dir>`, set to maturity `legacy` with `informs`, and locked (`muon ws sync --legacy`; ADR-009 §5, §15) |

Port / refactor / rewrite:
- **refactor in place**: code is sound, in the right language and runtime; the problem is structure.
- **port**: logic is valuable; language, runtime or structure is wrong.
  Import history (`git filter-repo` / `git subtree`) so the provenance survives.
- **rewrite from spec**: legacy serves only as a behaviour reference and a golden-data
  source. *(Decision for DAQ, 2026-10.)*

## 5. Legacy Code Rules

- Legacy projects are read-only references (enforced on disk, ADR-009 §15). Never a build or runtime
  dependency of new code. Run them only from an out-of-tree build directory.
- Knowledge extracted from legacy code goes into the as-is spec, not into
  comments copied along with the code.
- Copying legacy code into a new project must record its source (repo, path,
  commit).
- Inventory: `platform/docs/legacy_inventory.md`.

## 6. Multi-Agent Rules

- Top-level agents (workspace root) handle architecture, proposals,
  integration, and manifest PRs. Component agents (inside one project) do implementation
  against the pinned contracts.
- Parallel agents use separate git worktrees or branches. They never share a
  working tree.
- Contracts are frozen before parallel producer and consumer work starts.
- Humans own merges to `platform` docs, ADRs and `contracts`.
- Definition of done: tests and `muon verify` pass, specs and docs are
  updated, tests reference spec IDs.

## 7. Requirement IDs

- Projects own their requirement IDs (e.g. `FR-001` in `daq/doc/feature-requirements.md`).
  Outside the project, qualify them with the project name: `daq:FR-001`.
- Platform-level requirements in `docs/requirements/` use `<AREA>-<NNN>` (e.g. `SYS-001`, `HV-001`),
  assigned as each domain enters its iteration.
- IDs are never reused or renumbered. Retired IDs are marked as removed.

## 8. Prototype Lane

> Revised by ADR-012 §6: the prototype lane is the default for all work; “`contracts/`” below now
> means shared system contracts, staged in `core/contracts/system/` until extraction.

Early development is often bottom-up and exploratory inside one repository. Inside a single
`incubating` or `active` repository, prototyping:

- needs **no** platform change proposal and no top-level process. The repository's own
  `AGENTS.md` governs (e.g. DAQ's prototype-first workflow);
- may happen in the shared workspace, or in a plain clone of that repository (ADR-012 §5);
- still respects the legacy guardrails (ADR-009 §15) and never copies cross-repo contracts locally.

A change proposal (§3) becomes necessary when:

1. a contract in `contracts/` must change or be added; or
2. prototype behaviour is promoted into the spec baseline. What the prototype taught is then
   written as spec deltas with acceptance criteria. This is the "spike → spec" step.
