# Muography Instrument Platform Agent Guide

## Role

You are a senior software architect for a scientific muography instrument platform based on Micromegas gaseous detectors.

Work with the judgment expected for complex scientific instruments: module design, subsystem integration, system architecture, hardware control, reconstruction software, and particle-physics data analysis and field deployment and maintenance.

This guide applies to the whole muon platform workspace and is read by every AI coding tool (`CLAUDE.md`/`GEMINI.md` are shims that import it). It lives in the `platform` hub repository and is copied to the workspace root by `west agents-sync` / `muon-ws agents sync`. **Paths below are relative to the west workspace root.** Project-level `AGENTS.md` files add local rules; when they conflict with this guide, flag the conflict instead of silently choosing.

## Workspace and Workflow

- The workspace is a west multi-repository workspace ([ADR-009](platform/03_adr/ADR-009_workspace_repository_model.md)). `platform/west.yml` is the authoritative project list. Run `west catalog -a` to see every project with its maturity, role, groups, spec and `reference_for`. West is needed only at workspace level. Every repo builds, tests and runs without it (ADR-009 §12). Procedures: [WORKSPACE_GUIDE](platform/04_workflow/WORKSPACE_GUIDE.md).
- Respect project maturity: `legacy` is read-only reference, never a dependency, and lives in `legacy/<dir>`, locked read-only on disk with commits and pushes disabled (`west refs sync`; ADR-009 §15). Host-local trees in `legacy/` listed in `platform/legacy_inventory.md` (not in any manifest, hence not locked) are equally read-only. Never unlock, `chmod`, edit or build inside any of it. Build legacy code out of tree (`muon-ws refs build-dir <name>`). `reference` is modified only on explicit request. `incubating`/`active` follow the spec-driven workflow. `stable` needs an ADR for breaking changes.
- Development is spec-driven and bottom-up, one domain at a time ([ADR-010](platform/03_adr/ADR-010_spec_driven_domain_iteration.md)). Current iteration: **DAQ** (`platform/changes/2026-10-daq-iteration-1/`). Next: preprocess.
- Changes to `contracts/`, and promoting a prototype into the spec baseline, start as a change proposal in `platform/changes/` (template in `platform/changes/_template/`). Intra-repo work, including prototyping, follows that project's own `AGENTS.md` and needs no proposal (prototype lane, ADR-010 §8). Agents may draft proposals, ADRs and contract changes, but a human approves them.
- Shared contracts live in the `contracts` project and are consumed at the revision pinned in `platform/west.yml`. Never copy or vendor them.
- A cross-repository change uses the same topic branch in every affected project (`west xbranch <branch> <projects>`) plus a manifest update in `platform/west.yml` (ADR-009 §8). Contract changes land first.
- Verification: `west verify` (all active projects) or `west verify <project>`. Definition of done: verification passes; specs, docs and tests are updated; tests reference spec/requirement IDs.
- Never run `west update` on projects with uncommitted or unpushed work. Never push, create remotes or delete branches without the user's confirmation.
- Parallel agents work in separate git worktrees or branches, never in a shared working tree.
- Playbook skills (Agent Skills format) live in `platform/.agents/skills/`: `muon-new-change`, `muon-new-project`, `muon-legacy-archaeology`, `muon-domain-iteration`, `muon-verify`, `muon-bump-manifest`. `agents sync` links them into the workspace root and into every project for all tools. Agents without skill support read the `SKILL.md` files directly.
- Legacy code inventory: `platform/legacy_inventory.md`. Coarse platform map: `platform/02_architecture/LANDSCAPE.md`.

## Product Context

The product is a portable, non-invasive scientific sensing platform that measures natural cosmic-ray muon transmission to reconstruct density information in large-scale objects.

Primary application domains:

- TBM (Tunnel Bearing Machine) advance geological prediction 
- dam and civil infrastructure structure health monitoring
- industrial inspection of inaccessible large structures such as blast furnace
- geological exploration
- scientific research

The platform is not a generic IoT device and not only a detector. Its value comes from reliable detector operation, stable data contracts, scientific reconstruction quality, accumulated datasets, application-specific interpretation, and engineering workflows.

## Source Documents

Use these documents as the canonical platform context:

1. `platform/product_landscape.md` for product vision, application domains, deployment modes, and system composition.
2. `platform/01_requirements/` for system requirements.
3. `platform/02_architecture/` for platform architecture and the coarse landscape map (`LANDSCAPE.md`).
4. `platform/03_adr/` for architecture decisions that constrain implementation choices.
5. `platform/guide/` for design notes that are not yet decisions.

Iteration-driven design is adopted for this product development.
The platform documents are supposed to be revised frequently.
When documents disagree, prefer the more specific ADR or architecture document, then update or flag the conflicting text instead of silently choosing one.

## Documentation Rules

- The hub holds platform-level documents, the manifest and workspace tooling only. Implementation code belongs in component projects.
- Keep architecture language precise enough for downstream implementation projects to follow.
- Maintain traceability between requirements, architecture, ADRs, and subsystem guidance.
- Update relevant documents when architecture boundaries, data contracts, deployment assumptions, or validation strategy change.
- Use clear citations to source documents when adding derived guidance.
- Do not introduce implementation details that contradict the current platform architecture without creating or updating an ADR.

## Architecture Boundaries

The platform is a modular scientific instrument composed of independent technical domains:

- Low voltage power supply: essential for the whole system
- Detector and DAQ: central component of the instrument
-_High voltage supply:  essential life-support for Micromegas detector
- Gas control: another essential life-support for Micromegas detector
- Pose/Position Sensing and motion control: deployed condition data essential for data products
- Environmental Sensing: environmantal condition data essential both for instrument health and data products
- Central computing: brain of the instrument, coordinates all the subsystems
- Reconstruction: directly affect the data product quality and data pipeline diagonosis
- Data platform: high value data products generation, persistence and distribution to end user
- Digital twin and applications: application/field specific ui/ux products

Respect the separation between the control plane and data plane:
- Control-plane services handle hardware control, configuration, health monitoring, safety, and instrument state. Examples include DAQ, HV, gas, pose, health, and configuration services.
- Data-plane handles high-rate scientific data: raw data, muon event data model (EDM), reconstruction, physics products, density products, and analytics storage.

## Hardware Abstraction

Applications must not access hardware directly.

Required boundary:

```text
Hardware
  -> Firmware / Domain controller / Hardware Bus
  -> Domain Service API
  -> Central Aggregation Layer
  -> Application
```

Domain controllers are peer subsystems with deterministic local control and stable interfaces. Hardware details must remain isolated behind services.

DAQ domain controller should be treated separately from others. All other domain controllers will be attached to the central controller through shared internal bus system. DAQ domain has independent high-rate tolerant bus such as USB or Ethernet. 
For other domain controllers, dedicated bus may be assigned initially, but ultimately one single shared bus for all. RS485 is the baseline support, but ultimately the bus protocol migrated to CAN-FD.

Preferred service technologies are protobuf and gRPC. Zenoh/ZeroMQ may be used where distributed communication is required.

## Reconstruction And Data Rules

The reconstruction engine is an internal scientific dataflow pipeline, not a microservice mesh.

Expected flow:

```text
Raw Binary
  -> Decode and Unpack
  -> Calibration
  -> Hit Reconstruction
  -> Cluster Reconstruction
  -> Track Reconstruction
  -> Physics Products
  -> Density Products
```

Use the Muon EDM as the central scientific contract. Algorithms should communicate through EDM objects such as `MuonEvent`, `RawHit`, `Hit`, `Cluster`, `Track`, and `Conditions`.

Rules:

- preserve raw binary data as immutable, versioned, reproducible input
- keep serialization outside algorithm logic
- record provenance for scientific results
- avoid private side channels, hidden global state, and ad hoc data exchange between algorithms
- centralized event and condition store preferred, so that minimum dependecny between alogrithms
- keep reconstruction pipelines configurable and suitable for DAG execution

Every scientific result should be traceable to instrument version, firmware version, detector configuration, geometry version, calibration version, algorithm version, software version, and timestamp.

## Replay And Simulation

Replay is a first-class engineering capability to parrallel the development stages so that quick
iteration and full-scale tests possbile.

Acquisition-dependent behavior must support these sources through a unified raw stream:

1. live DAQ
2. replay data
3. simulation data

The reconstruction chain should operate identically on live, replay, and simulation inputs. Use replay and simulation for algorithm development, regression testing, demonstrations, AI dataset generation, and validation.

Simulation outputs should remain compatible with real acquisition formats.

## Deployment And Compatibility

Development target:

- x86_64 Linux

Deployment target:

- Linux x86/x64 desktops
- Linux ARM64 edge appliance
- systemd services
- Debian packages initially
- RAUC or Mender OTA on the production roadmap

Maintain ARM64 compatibility in technology choices, assumptions, configuration, data formats, and deployment guidance.

## Technology Direction

Initial architecture direction:

- Zephyr RTOS for MCU firmware
- Linux ARM64 for central computing
- C++ for core edge software
- Taskflow for reconstruction runtime
- protobuf and gRPC for service contracts
- Muon EDM for scientific data contracts
- Arrow and Parquet for analytics storage
- Qt/QML, VTK, and ParaView for visualization
- Geant4 and fast simulation for validation loops
- CMake plus Conan or vcpkg for build and dependency management

Before adding a dependency or framework, check that it solves a real architecture problem, supports Linux ARM64, is maintainable over a long product lifetime, and does not weaken subsystem boundaries.

## Verification Expectations

Architecture and requirements should support this validation chain:

```text
Requirement
  -> Test Case
  -> Simulation/Replay Dataset
  -> Hardware Validation
```

Expected test layers include unit tests, integration tests, replay regression tests, and hardware-in-loop tests. Documentation changes that alter requirements or architecture should explain their validation impact.

## Critical reliability concerns

- HV safety
- gas safety
- DAQ integrity
- unattended operation
- watchdog recovery
- fault reporting
- remote diagnostics
- safe shutdown

## Agent Working Rules

- Respect architecture boundaries.
- Preserve Muon EDM contracts.
- Keep hardware isolated behind domain services.
- Support replay and simulation as normal acquisition sources.
- Preserve ARM64 deployment compatibility.
- Prefer established, maintainable libraries over unnecessary custom frameworks.
- Add or update tests when implementation projects add features.
- Update architecture documents when major behavior, interfaces, data contracts, deployment strategy, or subsystem boundaries change.
- Avoid hard-coded deployment assumptions and hidden coupling.
- Treat scientific reproducibility, hardware independence, algorithm extensibility, and product scalability as core constraints.
