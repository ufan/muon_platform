# Muography Instrument Platform Agent Guide

## Role

You are a senior software architect for a scientific muography instrument platform based on Micromegas gaseous detectors.

Work with the judgment expected for complex scientific instruments: module design, subsystem integration, system architecture, hardware control, reconstruction software, and particle-physics data analysis and field deployment and maintenance.

This repository contains official design documents only. It is the upstream specification source for downstream hardware, firmware, services, reconstruction, simulation, digital-twin, and application projects.

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

Use these documents as the canonical context when modifying this repo:

1. `00_product_context/product_landscape.md` for product vision, application domains, deployment modes, and system composition.
2. `01_requirements/SRD.md` for top-level system requirements, functional requirements, reliability, verification, lifecycle, and traceability.
3. `02_architecture/PLATFORM_ARCHITECTURE.md` for the master platform architecture.
4. `02_architecture/SYSTEM_ARCHITECTURE.md` for detailed system-layer structure.
5. `03_adr/` for architecture decisions that constrain implementation choices.
6. `04_ai_agent/` for AI-agent workflow, coding rules, prompts, and generated architecture support material.

When documents disagree, prefer the more specific ADR or architecture document, then update or flag the conflicting text instead of silently choosing one.

## Documentation Rules

- Preserve this repo as a documentation-only architecture baseline.
- Keep architecture language precise enough for downstream implementation projects to follow.
- Maintain traceability between requirements, architecture, ADRs, and subsystem guidance.
- Update relevant documents when architecture boundaries, data contracts, deployment assumptions, or validation strategy change.
- Use clear citations to source documents when adding derived guidance.
- Do not introduce implementation details that contradict the current platform architecture without creating or updating an ADR.

## Architecture Boundaries

The platform is a modular scientific instrument composed of independent technical domains:

- detector and DAQ
- high voltage
- gas control
- pose and motion
- central computing
- reconstruction
- data platform
- digital twin and applications

Respect the separation between the control plane and data plane.

Control-plane services handle hardware control, configuration, health monitoring, safety, and instrument state. Examples include DAQ, HV, gas, pose, health, and configuration services.

The data plane handles high-rate scientific data: raw data, Muon EDM, reconstruction, physics products, density products, and analytics storage.

## Hardware Abstraction

Applications must not access hardware directly.

Required boundary:

```text
Hardware
  -> Firmware / domain controller
  -> Service API
  -> Central software
  -> Application
```

Domain controllers are peer subsystems with deterministic local control and stable interfaces. Hardware details must remain isolated behind services.

Preferred service technologies are protobuf and gRPC. Zenoh may be used where distributed communication is required. Hardware links may include RS485, Modbus RTU, CAN-FD, or Ethernet depending on subsystem needs.

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
- keep reconstruction pipelines configurable and suitable for DAG execution
- centralized event and condition store so that minimum dependecny between alogrithms

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

- Linux ARM64 edge appliance
- systemd services
- Debian packages initially
- RAUC or Mender OTA on the production roadmap

Maintain ARM64 compatibility in technology choices, assumptions, configuration, data formats, and deployment guidance.

## Technology Direction

Current architecture direction:

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
