# Repository model

Repository boundaries, dependency directions and contract ownership. Binding; rationale in
[ADR-015](../adr/ADR-015_repository_and_instrument_layering.md). The actual repository list is
`platform/repos/*.repos` (`muon list`). Planned repositories are not existing dependencies.

## Repositories

| Repository | Responsibility |
|---|---|
| `muon_core` (`core/`) | Scientific domain: DAQ, preprocess, recon, conditions interpretation, scientific contracts, online/offline runners (shared library targets). |
| Domain repositories (planned: HV, gas, LV, pose, environment) | Firmware, domain service and simulator/fake with tests, one per independently developed subsystem. Created when the domain's iteration starts. |
| `muon_instrument` (planned) | Instrument state machine, sequencing, interlock policy, aggregation/API gateway, operator CLI, product profiles and operational configuration. Its release manifest is the product bill of materials. |
| `muon_contracts` (`contracts/`) | Shared system contracts. Placeholder: drafts live in `core/contracts/system/` until extraction. |
| Conditions payloads (planned at preprocess) | Append-only detector/site payload versions (mapping, topology, geometry, alignment), seeded from `legacy/config`. Schemas and interpretation stay in core. |
| `muon_platform` (`platform/`) | Requirements, architecture, decisions, workflow, change records, repository manifests, the `muon` tool and agent skills. No product code. |
| `muon_testdata` (`testdata/`) | Dataset catalog and tool; bytes stay local and immutable ([ADR-011](../adr/ADR-011_test_data.md)). |
| `study/`, `tools/*` | Support; changed only on explicit request. |
| `legacy/*`, `archive/*` | Read-only references, never dependencies ([legacy inventory](../legacy_inventory.md)). |

Also planned outside core: detector front-end firmware and offline applications (imaging/density,
data platform, digital twin). Physics simulation is a separate project, not part of this platform
(ADR-008). They use core packages and contracts, never copies.

## Dependencies

| Consumer | May depend on |
|---|---|
| System contracts | Nothing. |
| Domain repositories | System contracts only; never another domain or core. |
| Core | System contracts; sensor data only through telemetry/conditions contracts. |
| Instrument | System contracts and the domain and core service APIs (generated clients). |
| Offline applications | Core packages and contracts. |
| Conditions payloads | Core schemas, for validation only. |
| Platform | Nothing at build time. |

## Contract ownership

| Contract | Owner |
|---|---|
| Raw capture, EDM, pipeline records, DAQ API and device FSM | `core/contracts/science/` |
| Domain-service pattern, telemetry catalog, time base, conditions interchange, product-profile schema | `core/contracts/system/` until extraction to `contracts/` |
| Device ↔ host wire protocol | `core/daq/ref/<target>/` |
| Conditions payload schemas and interpretation | Core |

## Splitting and extraction

- Split a repository only when toolchain, lifecycle or audience differs. A different deployment
  target is a packaging concern; successive processing stages are not a reason to split.
- When a second domain or the first instrument starts, extract `core/contracts/system/` into
  `muon_contracts` with history, publish semver tags and check breaking changes in its CI.
- Create the conditions payload repository when preprocess starts.
