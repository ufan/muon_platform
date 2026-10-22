# ADR-010 Spec-Driven Domain Iteration

Version: 1.0
Status: Accepted (2026-10-21)
Extends: ADR-006 §4 "Specification Driven Development"
Related: ADR-008 (replay), ADR-009 (workspace model)
Revised: 2026-10-21 (§8 prototype lane; §4 step 8)

## 1. Decision Summary

The platform is built **bottom-up, one domain at a time**, from a coarse
global landscape (`02_architecture/LANDSCAPE.md`). Each domain goes through a
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
| Requirement | `platform/01_requirements/` | prose with stable IDs (§7) |
| Architecture / decision | `platform/02_architecture/`, `platform/03_adr/` | prose |
| Component spec | `<project>/SPEC.md` | behaviour and acceptance criteria referencing requirement IDs |
| Contract | `contracts/` | machine-readable: ASN.1 wire, schemas, OpenAPI/AsyncAPI or protobuf, state-machine tables |
| Conformance | `<project>/tests/` | generated code, contract tests |
| Behaviour | `<project>/tests/`, replay datasets | golden-data and replay tests (ADR-008) |

Tests name the spec or requirement IDs they cover.

## 3. Change Lifecycle

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
5. **Verify**: `west verify` for the affected groups; contract, unit and golden tests.
6. **Archive**: deltas are merged into the living specs. The proposal moves to
   `changes/archive/`.

## 4. Domain Iteration Playbook

| Step | Output |
|---|---|
| 0. Scope | boundary of the domain in `LANDSCAPE.md`; "downstream needs" of its outputs |
| 1. Legacy archaeology | **as-is spec**: inputs, outputs, file formats, calibration dependencies, failure modes, implicit physics/hardware knowledge |
| 2. Golden data (ADR-011) | recorded inputs and legacy (or hardware) outputs with tolerances; where legacy cannot run, recorded hardware captures plus hand-checked expectations |
| 3. To-be spec and contracts | spec deltas, provisional contracts, ADRs for significant choices, and the **port / refactor / rewrite** decision |
| 4. Skeleton and failing tests | interfaces, contract tests, golden comparisons |
| 5. Implement | port, refactor or rewrite |
| 6. Differential verification | output matches legacy/golden data except for **documented, intentional deviations** |
| 7. Strangler switch | the new domain replaces legacy in the chain; its contracts are promoted |
| 8. Retire | the old repository is frozen (tag `legacy-final`), moved to `legacy/<dir>`, set to maturity `legacy` with `reference_for`, and locked (`west refs sync`; ADR-009 §5, §15) |

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
- Inventory: `platform/legacy_inventory.md`.

## 6. Multi-Agent Rules

- Top-level agents (workspace root) handle architecture, proposals,
  integration, and manifest PRs. Component agents (inside one project) do implementation
  against the pinned contracts.
- Parallel agents use separate git worktrees or branches. They never share a
  working tree.
- Contracts are frozen before parallel producer and consumer work starts.
- Humans own merges to `platform` docs, ADRs and `contracts`.
- Definition of done: tests and `west verify` pass, specs and docs are
  updated, tests reference spec IDs.

## 7. Requirement IDs

- Projects own their requirement IDs (e.g. `FR-001` in `daq/doc/feature-requirements.md`).
  Outside the project, qualify them with the project name: `daq:FR-001`.
- Platform-level requirements in `01_requirements/` use `<AREA>-<NNN>` (e.g. `SYS-001`, `HV-001`),
  assigned as each domain enters its iteration.
- IDs are never reused or renumbered. Retired IDs are marked as removed.

## 8. Prototype Lane

Early development is often bottom-up and exploratory inside one repository. Inside a single
`incubating` or `active` repository, prototyping:

- needs **no** platform change proposal and no top-level process. The repository's own
  `AGENTS.md` governs (e.g. DAQ's prototype-first workflow);
- may happen in a standalone clone or a repo-rooted workspace (ADR-009 §12–§13);
- still respects the legacy guardrails (ADR-009 §15) and never copies cross-repo contracts locally.

A change proposal (§3) becomes necessary when:

1. a contract in `contracts/` must change or be added; or
2. prototype behaviour is promoted into the spec baseline. What the prototype taught is then
   written as spec deltas with acceptance criteria. This is the "spike → spec" step.
