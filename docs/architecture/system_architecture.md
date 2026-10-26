# System architecture

The components, boundaries and data flow of the muography instrument. This document is binding;
change it together with the decision behind the change (ADR or decision log). Targets described here
are not claims of implementation; component specifications state what exists.

## 1. Principles

- Hardware stays behind domain services. Applications and orchestration never address devices
  ([ADR-003](../adr/ADR-003_hardware_domain_services.md), [ADR-005](../adr/ADR-005_hardware_abstraction.md), [ADR-014](../adr/ADR-014_slow_control_domains_and_transports.md)).
- Domain controllers own deterministic control, safety and interlocks; central software orchestrates.
- The instrument commands every domain, core included; core never commands another domain
  ([ADR-012](../adr/ADR-012_repository_baseline_and_workflow.md)).
- Control, scientific data and telemetry are separate planes (§4). Sensor data reaches algorithms
  only as immutable conditions.
- Raw data is immutable, and every scientific product is traceable to its inputs (§6).
- Live, replayed and simulated acquisition feed one raw-stream contract; online and offline
  processing share code ([ADR-008](../adr/ADR-008_simulation_verification_replay.md)).
- Algorithms exchange Muon EDM objects inside a DAG runtime, not through services
  ([ADR-001](../adr/ADR-001_reconstruction_runtime.md), [ADR-002](../adr/ADR-002_muon_edm_serialization.md)).
- Linux ARM64 stays supported.

## 2. Composition

```text
Micromegas detector -> front-end/FPGA -> DAQ -> scientific pipeline -> data products
                                          |                              |
                               immutable raw archive          applications / digital twin

HV / gas / LV / pose / environment -> domain services -> instrument coordination
                  |                                              |
            telemetry archive <---------------------------- status and operation
                  |
          conditions providers -> scientific pipeline
```

| Domain | Responsibility |
|---|---|
| DAQ | Detector readout and device control, high-rate transport, raw capture and acquisition metadata. |
| HV | Bias generation, ramping, voltage and current measurement, protection. |
| Gas | Flow regulation, pressure monitoring, protection. |
| LV | Power for the instrument electronics. |
| Pose | Detector orientation and position. Active motion control is not required. |
| Environment | Pressure, temperature and humidity. |
| Instrument | Operating modes, sequencing, interlock policy, service aggregation and operator access. |
| Core | DAQ, preprocess, event building, reconstruction and conditions interpretation (one repository). |
| Applications | Imaging/density, analysis, visualization, digital twin and reporting. |

Cooling and dehumidification are out of scope. Repository boundaries: [repository model](repository_model.md).

## 3. Control and services

```text
Application -> instrument -> domain service API
            -> domain controller (host software adapter, or on-board controller via a host proxy)
            -> transport (configured per device) -> hardware
```

- Domain services expose typed operations plus lifecycle, status, health, alarms and capabilities,
  with a simulator or fake backend for tests. The interface does not change when a transport or
  controller form changes.
- Service interfaces use protobuf/gRPC. Other messaging (Zenoh, ZeroMQ) needs a demonstrated use.
- DAQ uses a dedicated high-rate link (USB today) and is never on a slow-control bus.
- Slow control ([ADR-014](../adr/ADR-014_slow_control_domains_and_transports.md)): devices are Modbus
  RTU slaves on host RS-485 ports. A versioned device map assigns each device to a domain and
  transport, so port count, port names and grouping are configuration. One bus owner serialises each
  port. A custom protocol and CAN-FD are later aspirations.

## 4. Information planes

| Plane | Content |
|---|---|
| Control | Commands, operating modes, configuration, lifecycle, safety and health. |
| Scientific data | Raw capture → validated records → EDM objects → products. |
| Telemetry | Continuous operating measurements and pose, archived and resolved into conditions. |

DAQ takes part in control and scientific data; telemetry and raw detector traffic do not share a transport.

## 5. Scientific data path

The module chain, contract owners and downstream needs are in the [architecture overview](architecture_overview.md).

- Preprocess validates transport records (framing, CRC, malformed or lost frames). Raw bytes never
  reach event building.
- Recon owns event building and reconstruction. The published event frame is the canonical handoff;
  diagnostics and metrics are side outputs. The event-builder spec is staged in
  [core](../../../core/daq/doc/specs/event-builder.md) until the recon module exists.
- Reconstruction is a configurable DAG (Taskflow initially). Algorithms consume EDM objects and
  immutable conditions; serialization stays outside algorithm logic.
- Products: hits, clusters, tracks, rates, angular and flux distributions, opacity/density estimates,
  each with quality and uncertainty. Analytics storage uses Arrow/Parquet.

## 6. Conditions, time and provenance

- Conditions combine the detector model, assembly and deployment geometry/alignment, calibration
  and telemetry-derived intervals into an immutable snapshot with an ID and content hash. Core owns
  schemas and interpretation ([conditions](../../../core/docs/conditions.md)).
- Online, a live provider supplies and records current values; offline, a builder derives versioned
  intervals from the telemetry archive. Algorithms never query telemetry.
- The edge appliance clock is the only common time reference (monotonic time with `boot_id`, UTC,
  sync state). Device clocks map to it through correlation records with an uncertainty; the budget
  is about 1 s.
- Every product records instrument and firmware identity, software (core) revision, algorithm
  version and parameters, conditions snapshot ID and hash, and time. A conditions override keeps
  both identities.

## 7. Replay, simulation and digital twin

- Replay and simulation produce the same raw-stream contract as live acquisition. Decoding,
  validation, event building, schemas and publishing are identical in every mode; only the source
  adapter's pacing, clock, backpressure and sink policies differ, and they are recorded in metadata
  ([acquisition sources](../../../core/daq/doc/specs/acquisition-sources.md)).
- Golden datasets are versioned and immutable ([ADR-011](../adr/ADR-011_test_data.md)).
- Simulation (Geant4 plus fast detector response) produces DAQ-format output and synthetic truth.
  It does not replace hardware acceptance.
- The digital twin links object geometry, detector deployment, products, density fields and
  interpretation, with consistent model identities across simulation, reconstruction and display
  ([ADR-007](../adr/ADR-007_digital_twin_strategy.md)).

## 8. Deployment and technology

- Develop on Linux x86_64; deploy on Linux desktops and ARM64 edge appliances, with systemd and
  Debian packages. Atomic OTA and fleet management are later ([ADR-004](../adr/ADR-004_deployment_and_updates.md)).
- Firmware: Zephyr on MCU controllers; FPGA for detector front-end processing.
- Software: C++ and CMake, Taskflow, protobuf/gRPC, Muon EDM, Arrow/Parquet; Qt/QML, VTK and
  ParaView for visualization.
- Add a dependency only when it solves a real problem, supports ARM64 and does not weaken a boundary.

## 9. Verification

Requirements trace to unit and contract tests, replay/golden comparisons, simulation and
hardware-in-the-loop tests. Tests name the requirement IDs they cover. A passing build or replay is
not evidence of verified detector behaviour; report checks not performed.

## 10. Open points

| Topic | State |
|---|---|
| Slow-control service interfaces | Deferred. When started: transport-independent, Modbus host adapters first, and each domain states which protection lives in the device and which in its controller. |
| C++ standard | Component builds decide (C++17 toolchain today); no workspace-wide standard yet. |
