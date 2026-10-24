# Engineering Context for Agents

Product, architecture and engineering rules that apply to every repository. They moved here from
`platform/AGENTS.md` to keep the always-loaded rules short (ADR-012 §7). Read this before design
or architecture work, and when a task touches boundaries, contracts, data or deployment.

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

1. `platform/docs/product_landscape.md` for product vision, application domains, deployment modes, and system composition.
2. `platform/docs/requirements/` for system requirements.
3. `platform/docs/architecture/readme.md` selects the architecture view: `architecture_overview.md`
   for the coarse map, `system_architecture.md` for detailed system design, and `repository_model.md`
   for repository boundaries/dependencies.
4. `platform/docs/adr/` for architecture decisions that constrain implementation choices.
5. `platform/docs/guide/` for design notes that are not yet decisions.

Reading order and index: `platform/docs/README.md`.

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
- High voltage supply:  essential life-support for the detector
- Gas control: another essential life-support for the detector
- Pose/Position Sensing and motion control: deployed condition data essential for data products; in the future, an active actuator may be integrated
- Environmental Sensing: environmantal condition data essential both for instrument health and data products, such as atomosphere pressure, temperature, humidity etc.
- Central computing: brain of the instrument, coordinates all the subsystems
- Motion Control: 
- Reconstruction: directly affect the data product quality and data pipeline diagonosis
- Data platform: high value data products generation, persistence and distribution to end user
- Digital twin and applications: application/field specific ui/ux products

The detailed design is in `architecture/system_architecture.md`. Keep its three information planes separate:
- Control-plane services handle hardware control, configuration, health monitoring, safety, and instrument state. Examples include DAQ, HV, gas, pose, health, and configuration services.
- Data-plane handles high-rate scientific data: raw data, muon event data model (EDM), reconstruction, physics products, density products, and analytics storage.
- Sensor/telemetry measurements are archived and resolved into conditions before scientific algorithms consume them.

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
