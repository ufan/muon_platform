# Repository model

Status: current architecture. Paths are relative to the workspace root.

This document describes repository boundaries and allowed dependencies. Decision rationale:
[ADR-012 §3–§4 and §6](../adr/ADR-012_repository_baseline_and_workflow.md).
The [architecture overview](architecture_overview.md) describes scientific data flow and domain boundaries.
The actual repository list and maturity metadata live in `platform/repos/*.repos` and each
repository's `.muon/repo.yml` (`muon list`). Planned repositories below are not existing dependencies.

## Responsibilities

| Repository / path | Responsibility and state |
|---|---|
| `muon_core` / `core/` | Scientific domain: DAQ, scientific contracts, conditions interpretation, preprocess, reconstruction and online/offline runners. DAQ, preprocess and recon are modules within core. Online and offline share library targets. |
| Sensor domain repositories (planned: HV, gas, environment, pose, LV) | One repository per independently developed subsystem: firmware, domain service and simulator/fake with tests. Created when that domain enters its iteration. |
| `muon_instrument` (planned) | Coordination: instrument state machine, sequencing, interlock policy, aggregation/API gateway, CLI, product profiles, operational configuration and integration validation. Starts with `products/<name>/`; its release manifest is the product bill of materials. |
| `muon_contracts` / `contracts/` | Placeholder for shared system contracts. Drafts currently live in `core/contracts/system/` until extraction below. |
| Conditions payload repository (planned for preprocess) | Versioned detector/site payloads, seeded from read-only `legacy/config`: mapping, topology, geometry and alignment. Versions are append-only; schemas and interpretation belong in core. Telemetry-derived conditions and operational application settings do not belong here. |
| `muon_platform` / `platform/` | Requirements, architecture, decisions, guides, change records, repository manifests, workspace tooling and agent skills. No product code or build-time dependency on product repositories. |
| `muon_testdata` / `testdata/` | Dataset catalog and tooling. Dataset bytes remain local and immutable; see [ADR-011](../adr/ADR-011_test_data.md). Support maturity: changes require an explicit request. |
| `study/`, `tools/*` | Support studies and utilities; changes require an explicit request. |
| `legacy/*`, `archive/*` | Read-only references, never build or runtime dependencies. Managed legacy repositories are declared in `platform/repos/legacy.repos`; archives are host-local. See the [legacy inventory](../legacy_inventory.md). |

Detector front-end firmware, simulation and offline applications (imaging/density, data platform,
digital twin) are planned outside core. Where they consume scientific software, use core packages
and canonical contracts rather than copying their sources. Sensor-domain independence below still
applies; this does not permit sensor domains to depend on core.

## Dependency directions

An arrow means “depends on”; allowed service dependencies use generated API clients.

| Consumer | Allowed dependency / boundary |
|---|---|
| Shared system contracts | No dependency on domain implementations. |
| Sensor domains | Shared system contracts; never another domain implementation or core. |
| Core | Shared system contracts; sensor information arrives through telemetry/conditions contracts, not direct sensor control or implementation imports. |
| Instrument | Shared system contracts and domain/core service APIs. The instrument commands domains, including core. Core never commands another domain. |
| Offline applications | Core packages and canonical contracts. |
| Future conditions payload repository | Core schemas for validation only; no embedded algorithm or pipeline implementation. This does not authorize changing or building in `legacy/config`. |
| Platform | No product build-time dependencies. Workspace tooling manages repositories without becoming a product runtime dependency. |

System contracts are currently staged inside core; the shared-contract dependency direction is the
target boundary, not a requirement to import the placeholder `contracts/` repository today.
Sensor data reaches reconstruction only as immutable conditions snapshots. Conditions interpretation
is specified further in [core conditions guidance](../../../core/docs/conditions.md).

## Contract ownership

| Contract | Current owner |
|---|---|
| Scientific formats and objects: raw capture, EDM, pipeline records, DAQ API and device FSM | `core/contracts/science/`; evolve with their core consumers. |
| Domain-service pattern, telemetry catalog, time base, conditions interchange, product-profile schema | Drafts in `core/contracts/system/`; move to `contracts/` at the extraction trigger. |
| Device ↔ host wire protocol | DAQ hardware references in `core/daq/ref/<target>/`. |
| Conditions payload schemas, validation and interpretation | Core; payload versions live in the future payload repository. |

## Splitting and extraction

Split a repository when toolchain, lifecycle or audience/ownership differs. A different deployment
target alone is a packaging concern. Scientific modules are not separate repositories merely
because they represent successive processing stages.

When a second domain or the first instrument starts, extract `core/contracts/system/` into
`muon_contracts` with history preserved. Publish semver tags; consuming domains' `main` branches
pin tags, and contract CI checks breaking changes with `buf breaking` or schema diff.
Scientific contracts stay in core. Create the conditions payload repository at the start of preprocess.
These are existing triggers from ADR-012, not instructions to perform extraction now.

Keep this document current when repository boundaries or dependencies change, with links to the
relevant decision records. Workspace operations belong in the [developer guide](../workflow/DEVELOPER_GUIDE.md);
work discovery and session scope belong in the [work protocol](../../work/README.md).
