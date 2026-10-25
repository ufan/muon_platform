# Engineering Context for Agents

Status: current (always-read agent context; a summary that points to the owning documents).

Product, architecture and engineering rules that apply to every repository. They moved here from
`platform/AGENTS.md` to keep the always-loaded rules short (ADR-012 §7). Read this before design
or architecture work, and when a task touches boundaries, contracts, data or deployment.

## Product Context

The product is a portable, non-invasive scientific sensing platform that measures natural cosmic-ray muon transmission to reconstruct density information in large-scale objects.

Primary application domains:

- TBM (tunnel boring machine) advance geological prediction
- dam and civil infrastructure structure health monitoring
- industrial inspection of inaccessible large structures such as blast furnace
- geological exploration
- scientific research

The platform is not a generic IoT device and not only a detector. Its value comes from reliable detector operation, stable data contracts, scientific reconstruction quality, accumulated datasets, application-specific interpretation, and engineering workflows.

## Source Documents

Use these documents as the canonical platform context:

1. `platform/docs/requirements/SRD.md` for product vision, application domains, deployment modes and system requirements.
2. `platform/docs/architecture/readme.md` selects the architecture view: `architecture_overview.md`
   for the coarse map, `system_architecture.md` for detailed system design, and `repository_model.md`
   for repository boundaries/dependencies.
3. `platform/docs/adr/` for architecture decisions that constrain implementation choices.
4. `platform/docs/design/` for design notes (proposals, research, historical design records); each states its status.

Reading order and index: `platform/docs/README.md`.

Iteration-driven design is adopted for this product development, and the platform documents are
revised frequently. When documents disagree, authority comes from declared scope and status and from
explicit supersession (`platform/docs/README.md`), not from specificity or ADR number. Flag the
conflict instead of silently choosing one.

## Documentation Rules

- `platform/` holds platform-level documents, repository definitions and workspace tooling only. Implementation code belongs in component projects.
- Keep architecture language precise enough for downstream implementation projects to follow.
- Maintain traceability between requirements, architecture, ADRs, and subsystem guidance.
- Update relevant documents when architecture boundaries, data contracts, deployment assumptions, or validation strategy change.
- Use clear citations to source documents when adding derived guidance.
- Do not introduce implementation details that contradict the current platform architecture without creating or updating an ADR.

## Architecture Boundaries

The platform is a modular scientific instrument composed of independent technical domains:

- Low voltage power supply: essential for the whole system
- Detector and DAQ: central component of the instrument
- High voltage supply: essential life-support for the detector
- Gas control: another essential life-support for the detector
- Pose/Position Sensing and motion control: deployed condition data essential for data products; active motion control is an aspiration, not a requirement
- Environmental Sensing: environmental condition data essential both for instrument health and data products, such as atmospheric pressure, temperature and humidity
- Central computing: brain of the instrument, coordinates all the subsystems
- Reconstruction: directly affects data product quality and data pipeline diagnosis
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

Domain controllers are peer subsystems with deterministic control, safety and interlocks, behind stable domain service interfaces. A domain controller is either a host software adapter or an on-board controller. Hardware details must remain isolated behind services.

DAQ is separate: control and scientific data use a dedicated link (USB today), never a slow-control bus. Slow control follows [ADR-014](adr/ADR-014_slow_control_domains_and_transports.md): devices are Modbus RTU slaves on host RS-485 ports (three today, possibly fewer on a future single-board computer), grouped by assembly convenience; a versioned device map assigns them to domains, so ports and grouping are configuration. Custom HV/LV/gas boards start on Modbus RTU; a custom protocol and CAN-FD are later aspirations. Design domain service interfaces so that none of these changes affects them.

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
- prefer a centralized event and condition store, to minimize dependencies between algorithms
- keep reconstruction pipelines configurable and suitable for DAG execution

Every scientific result should be traceable to instrument version, firmware version, detector configuration, geometry version, calibration version, algorithm version, software version, and timestamp.

## Replay And Simulation

Replay is a first-class engineering capability that lets development stages proceed in parallel,
making both quick iteration and full-scale tests possible.

Acquisition-dependent behavior must support these sources through a unified raw stream:

1. live DAQ
2. replay data
3. simulation data

The reconstruction chain should operate identically on live, replay, and simulation inputs. Use replay and simulation for algorithm development, regression testing, demonstrations, AI dataset generation, and validation.

Simulation outputs should remain compatible with real acquisition formats.

## Deployment, Technology, Reliability And Verification

Details and qualifications live in `architecture/system_architecture.md` §8–§9; do not duplicate them here.
In short:

- Develop on x86_64 Linux; deploy to Linux desktops and Linux ARM64 edge appliances with systemd and
  Debian packages initially. Maintain ARM64 compatibility in technology choices, configuration, data
  formats and deployment guidance.
- Technology direction: Zephyr (MCU firmware), C++ with CMake, Taskflow, protobuf/gRPC for services,
  Muon EDM for scientific data, Arrow/Parquet for analytics, Qt/QML/VTK/ParaView, Geant4. Before
  adding a dependency or framework, check that it solves a real architecture problem, supports
  Linux ARM64, is maintainable over a long product lifetime and does not weaken subsystem boundaries.
- Critical reliability concerns: HV and gas safety, DAQ integrity, unattended operation, watchdog
  recovery, fault reporting, remote diagnostics and safe shutdown.
- Trace requirements to tests, replay/simulation datasets and hardware validation. Documentation
  changes that alter requirements or architecture should explain their validation impact.

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
