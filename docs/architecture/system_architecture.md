# System architecture

Status: current (binding).

The components, boundaries and data flow of the muography instrument. This document is binding;
change it together with the decision behind the change (ADR or decision log). Targets described here
are not claims of implementation; component specifications state what exists.

## 1. Principles

- Hardware stays behind domain services. Applications and orchestration never address devices
  ([ADR-003](../adr/ADR-003_hardware_domains_services_and_controllers.md), [ADR-014](../adr/ADR-014_hardware_domains_transports.md)).
- Domain controllers own deterministic control, safety and interlocks; central software orchestrates.
- The instrument commands every domain, core included; core never commands another domain
  ([ADR-015](../adr/ADR-015_repository_and_instrument_layering.md)).
- Control, scientific data and telemetry are separate planes (§4). Sensor data reaches algorithms
  only as immutable conditions.
- Raw data is immutable, and every scientific product is traceable to its inputs (§6).
- Live and replayed acquisition feed one raw-stream contract; online and offline processing share
  code ([ADR-008](../adr/ADR-008_data_sources_and_verification.md)).
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
| Applications | Application products (density inversion, anomaly maps, reports), visualization and digital twin; a layer above the scientific chain. |

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
- Slow control ([ADR-014](../adr/ADR-014_hardware_domains_transports.md)): devices are Modbus
  RTU slaves on host RS-485 ports. A versioned device map assigns each device to a domain and
  transport, so port count, port names and grouping are configuration. One bus owner serialises each
  port. A custom protocol and CAN-FD are later aspirations.

## 4. Information planes

| Plane | Content |
|---|---|
| Control | Commands, operating modes, configuration, lifecycle, safety and health. |
| Scientific data | Raw capture → validated records → EDM objects → products. |
| Telemetry | Continuous low-rate operating measurements and pose, stored locally first and then forwarded; resolved into conditions. |

DAQ takes part in control and scientific data; telemetry and raw detector traffic do not share a transport.

## 5. Scientific data path

The chain of scientific modules and the contracts between them. Updated at step 0 of every domain
iteration ([engineering process §1](../../governance/engineering_process.md#1-development-approach)).

### 5.1 Chain

```text
 detector ──USB/FX3──▶ daq ──raw stream──▶ preprocess ──board frames──▶ recon ──events/hits/tracks──▶ imaging
                        │                  (decode, CRC,               (event building,               (rates, flux,
                        │                   validation)                 hits, tracking)                opacity)
                        └──▶ raw persistence (immutable)                       └──▶ analysis
 replay ──same raw-stream contract──▶ preprocess …
```

daq, preprocess and recon are modules of `core`; the arrows are contracts in
`core/contracts/science/`. The device ↔ host wire protocol belongs to the DAQ hardware reference
(`core/daq/ref/<target>/`). Density inversion and other application products are a separate layer
downstream of imaging (§5.2).

| Module | Responsibility |
|---|---|
| daq | Command acquisition hardware; produce raw bytes and run metadata. |
| preprocess | Decode raw frames into validated board records (framing, CRC, malformed or lost frames). Raw bytes never reach event building. |
| recon | Build events and reconstruct hits, clusters and tracks from validated records and conditions. The published event frame is the canonical handoff; diagnostics and metrics are side outputs. The event-builder spec is staged in [core](../../../core/daq/doc/specs/event-builder.md) until the recon module exists. |
| imaging | Compute physics products from tracks: rates, angular flux, opacity. |
| analysis | Validate, calibrate and study outputs. |
| conditions | Resolve geometry, mapping, alignment, calibration and telemetry intervals into immutable snapshots (§6). |

Reconstruction is a configurable DAG (Taskflow initially). Algorithms consume EDM objects and
immutable conditions; serialization stays outside algorithm logic. Every product carries quality and
uncertainty. Analytics storage uses Arrow/Parquet.

### 5.2 Processing stages

The chain falls into three stages by purpose. Stages group modules; they are not modules.

| Stage | Content | Modules | Role |
|---|---|---|---|
| Event reconstruction | raw data → decoded records → events, hits, clusters, tracks | daq, preprocess, recon | mandatory; common to every application |
| Physics products | muography quantities: rates, angular flux, opacity | imaging | mandatory; the minimum value, common to every application |
| Application products | use-case products: density models, anomaly maps, risk indicators, reports | application layer, outside the scientific chain | value-added; may fuse other data (geology, BIM, surveys, telemetry) |

Event reconstruction and physics products run online and offline on shared code.

### 5.3 Downstream needs

Checked before an upstream contract is frozen.

| Contract | Consumers | Known needs | Open |
|---|---|---|---|
| Raw stream (daq → preprocess) | preprocess, persistence, replay | byte-exact capture, run metadata, loss markers | chunking for several, possibly disconnected consumers |
| Board frames (preprocess → recon) | event builder | event key, source/chip/channel identity, timestamps, validation flags ([draft](../../../core/contracts/science/pipeline/README.md)) | late, duplicate and timeout policy |
| Event frames (recon → downstream) | hit building, monitoring, persistence | status and reason, source coverage, host timestamps | schema, per-consumer payload |
| Tracks (recon → imaging, analysis) | imaging, analysis | direction, reference-plane position, fit quality, time | uncertainty model, selection flags |

### 5.4 Boundary test for a new module

Is it about bytes, records, events, tracks, studies or images? Does it produce or consume a
canonical contract? Can it run online, or only offline? If it spans more than one layer, the
boundary is too wide.

## 6. Conditions, time and provenance

- Conditions combine the detector model, assembly and deployment geometry/alignment, calibration
  and telemetry-derived intervals into an immutable snapshot with an ID and content hash. Core owns
  schemas and interpretation ([conditions](../../../core/docs/conditions.md)).
- Online, a live provider supplies and records current values; offline, a builder derives versioned
  intervals from the telemetry archive (gas state and gain factors, HV good-time intervals, pose
  segments). Algorithms never query telemetry.
- The edge appliance clock is the only common time reference (monotonic time with `boot_id`, UTC,
  sync state). Device clocks map to it through correlation records with an uncertainty; the budget
  is about 1 s, so no PTP is needed. The raw capture records `boot_id`, sync state and periodic
  correlation records.
- Every product records instrument and firmware identity, software (core) revision, algorithm
  version and parameters, conditions snapshot ID and hash, and time. A conditions override keeps
  both identities.

## 7. Offline data, replay and digital twin

- Offline datasets (`testdata`) are where single features and components iterate and are
  verified, run directly without the online pipeline ([ADR-008](../adr/ADR-008_data_sources_and_verification.md)).
- Replay mainly verifies the online pipeline. It produces the same raw-stream contract as live
  acquisition. Decoding, validation, event building, schemas and publishing are identical in every
  mode; only the source adapter's pacing, clock, backpressure and sink policies differ, and they are
  recorded in metadata
  ([acquisition sources](../../../core/daq/doc/specs/acquisition-sources.md)).
- Golden datasets are versioned and immutable ([ADR-011](../adr/ADR-011_test_data.md)).
- Physics simulation is not part of this project; a separate simulation project could feed the
  pipeline only through the raw-stream contract. Hardware domain simulators and fakes remain (§3).
- The digital twin links object geometry, detector deployment, products, density fields and
  interpretation, with consistent model identities across reconstruction and display
  ([ADR-007](../adr/ADR-007_digital_twin.md)).

## 8. Deployment and technology

- Develop on Linux x86_64; deploy on Linux desktops and ARM64 edge appliances, with systemd and
  Debian packages. Atomic OTA and fleet management are later ([ADR-004](../adr/ADR-004_deployment_and_updates.md)).
- Firmware: MCU-based domain controllers (RTOS not fixed); FPGA for detector front-end processing.
- Software: C++ and CMake, Taskflow, protobuf/gRPC, Muon EDM, Arrow/Parquet; Qt/QML, VTK and
  ParaView for visualization.
- Add a dependency only when it solves a real problem, supports ARM64 and does not weaken a boundary.

## 9. Verification

Requirements trace to unit and contract tests, offline-dataset/golden comparisons, online-pipeline
replay, domain-simulator integration and hardware-in-the-loop tests. Tests name the requirement IDs
they cover. A passing build or replay is not evidence of verified detector behaviour; report checks
not performed.

## 10. Open points

| Topic | State |
|---|---|
| Slow-control service interfaces | Deferred. When started: transport-independent, Modbus host adapters first, and each domain states which protection lives in the device and which in its controller. |
| Physics-products module (imaging) | Home not decided: core or its own repository. |
| C++ standard | Component builds decide (C++17 toolchain today); no workspace-wide standard yet. |
