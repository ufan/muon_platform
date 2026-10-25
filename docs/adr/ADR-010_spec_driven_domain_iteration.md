# ADR-010 Spec-driven domain iteration

Status: Accepted (2026-10-21; re-baselined 2026-10-25 to include the ADR-012 revisions)

## 1. Decision summary

- Build bottom-up, one domain at a time: DAQ → preprocess → recon → imaging/analysis; simulation
  and conditions alongside when needed.
- Each domain follows the playbook (§4), turning legacy code and domain knowledge into
  checkable specifications before implementation.
- New domains replace legacy stages one by one while the chain keeps working (strangler fig).
- Prototyping is the default (§8); specifications are updated when prototype behaviour becomes the baseline.

## 2. Specification layers

| Layer | Location | Form |
|---|---|---|
| Requirement | `platform/docs/requirements/`, component requirement files | prose with IDs (§7) |
| Architecture, decision | `platform/docs/architecture/`, `platform/docs/adr/` | prose |
| Component spec | `<repo>/SPEC.md`, `specs/` | behaviour and acceptance criteria citing requirement IDs |
| Contract | `core/contracts/`, later `contracts/`; device ↔ host protocol in `core/daq/ref/<target>/` | machine-readable schemas, protobuf, state tables |
| Conformance, behaviour | `<repo>/tests/`, golden and replay data | contract, golden and replay tests naming the IDs they cover |

## 3. Change proposals

Optional while prototyping. Write one in `platform/changes/<yyyy-mm>-<slug>/` (`proposal.md`,
`specs.md`, `contracts.md`, `tasks.md`) to record a decision, run a domain iteration, or promote a
prototype into the baseline. A human approves proposals, ADRs and contract changes; agents draft them.

## 4. Domain iteration playbook

| Step | Output |
|---|---|
| 0. Scope | the domain's boundary and the downstream needs of its outputs in [system architecture §5](../architecture/system_architecture.md#5-scientific-data-path) |
| 1. Legacy archaeology | as-is spec: inputs, outputs, formats, calibration dependencies, failure modes, implicit knowledge |
| 2. Golden data | recorded inputs and legacy or hardware outputs with tolerances ([ADR-011](ADR-011_test_data.md)) |
| 3. To-be spec and contracts | spec deltas, provisional contracts, ADRs for significant choices, and the port / refactor / rewrite decision |
| 4. Skeleton and failing tests | interfaces, contract tests, golden comparisons |
| 5. Implement | |
| 6. Differential verification | output matches golden data except for documented, intentional deviations |
| 7. Strangler switch | the new domain replaces the legacy stage; its contracts are promoted |
| 8. Retire | the old repository is tagged `legacy-final`, moved to `legacy/<dir>` and locked |

Refactor when the code is sound but badly structured; port (with history) when the logic is
valuable but the language or runtime is wrong; rewrite from spec when legacy is only a behaviour
reference and a golden-data source (chosen for DAQ).

## 5. Legacy code

Legacy code is a read-only reference, never a dependency, and runs only from out-of-tree builds.
Extracted knowledge goes into the as-is spec. Copied code records its source (repo, path, commit).
Inventory: [legacy inventory](../legacy_inventory.md).

## 6. Agents

Workspace-level sessions handle architecture, proposals and integration; repository-level sessions
implement against pinned contracts. Parallel writers use separate worktrees. Contracts are frozen
before producer and consumer work proceed in parallel. Done means tests and `muon verify` pass and
specs are updated.

## 7. Requirement IDs

- Repositories own their requirement IDs (`FR-001` in `core/daq/doc/feature-requirements.md`);
  outside the repository they are qualified: `daq:FR-001`.
- Platform requirements use `<AREA>-<NNN>` (`SYS-001`, `HV-001`), assigned when the domain enters
  its iteration.
- IDs are never reused or renumbered; retired IDs are marked removed.

## 8. Prototype lane

Inside one repository, prototyping needs no proposal; the repository's `AGENTS.md` governs. When
behaviour becomes the baseline, write the spec delta with acceptance criteria and requirement IDs
("spike → spec"). Legacy guardrails apply, and shared contracts are never copied locally.
