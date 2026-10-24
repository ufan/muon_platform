# System architecture

Status: current design baseline; not a claim of implemented or hardware-validated behavior.
Consolidated: 2026-10-24 from the former system and platform architecture specifications.

## 1. Scope and document boundaries

This document describes how the complete muography instrument's hardware, services, scientific
processing and applications interact. It supports survey/offline and continuous-monitoring/online
operation. Product mission, use cases and evolution belong in the [product landscape](../product_landscape.md);
requirements belong in the [SRD](../requirements/SRD.md) and subsystem specifications.

Read the [overview](architecture_overview.md) for the coarse map and downstream interface questions.
The [repository model](repository_model.md) owns repository boundaries, dependency directions and
contract locations. Component specifications, starting with [core](../../../core/SPEC.md), define
implementation acceptance. ADRs linked below preserve rationale; unresolved differences are listed
in §10 rather than resolved by document order or filename.

## 2. System composition

```text
Physical object and detector deployment
                  |
Micromegas detector -> front-end/FPGA -> DAQ -> scientific pipeline -> data products
                                         |                              |
                              immutable raw archive            applications / digital twin

HV / gas / pose / environment / LV -> domain services -> instrument coordination
                  |                                          |
            telemetry archive <------------------------ status and operation
                  |
          conditions providers -> scientific pipeline
```

The instrument coordinator orchestrates domains, operating modes, sequencing, interlocks and
external communication. Core processes scientific data; it does not command other domains.
Sensor information reaches reconstruction through conditions, not live device access.
These boundaries follow [ADR-003](../adr/ADR-003_instrument_service_architecture.md),
[ADR-005](../adr/ADR-005_hardware_abstraction.md) and
[ADR-012 §3–§4, §9](../adr/ADR-012_repository_baseline_and_workflow.md).

| Subsystem | Responsibility |
|---|---|
| Detector/front-end/FPGA and DAQ | Detector readout, device control, high-rate transport, raw capture and acquisition metadata. Hardware frames are not reconstructed host events. |
| HV | Bias generation, voltage ramping, current monitoring and local fault protection. |
| Gas | Gas supply, valve/flow regulation and relevant monitoring; detailed capabilities follow the gas requirements. |
| Pose/position | Orientation and location used to interpret measurements; active motion is future scope requiring a defined boundary (§10). |
| Environment | Pressure, temperature, humidity and other measured operating conditions. |
| LV | Power support for the instrument; detailed interfaces are specified with its domain. |
| Central computing / instrument | Service aggregation, coordination, processing runners, communications and operator access. Deterministic device control stays in domain controllers. |
| Scientific software | Preprocessing, event building, reconstruction, calibration interpretation and physics products. |
| Applications | Visualization, engineering analysis, density interpretation, reporting and digital twin integration. |

## 3. Services and communication

Applications access capabilities through services:

```text
Application -> instrument aggregation / domain API -> domain adapter
            -> transport -> domain controller / firmware -> hardware
```

Drivers, device registers and transport specifics remain behind the domain boundary. Local
controllers handle deterministic control and protection; central software handles orchestration.
Domain services expose lifecycle, status, health, alarms and capabilities, with simulator/fake
backends for testing. This service separation does not turn scientific algorithms into services.

Protobuf/gRPC is the preferred service interface. DAQ needs a separate high-rate transport such as
USB/FX3 or Ethernet; CAN-FD is not the raw DAQ stream transport. Slow-control bus details belong in
the [instrument management bus specification](../requirements/instrument_management_bus_requirement.md).
RS-485 is its current baseline; the intended CAN-FD evolution and DAQ management participation
need reconciliation as noted in §10. Optional messaging technologies are selected for demonstrated
needs, not required by this diagram. Rationale: ADR-003 and ADR-005.

## 4. Three information planes

| Plane | Content and path |
|---|---|
| Control | Commands, operating modes, configuration, lifecycle, safety and health through instrument/domain services. |
| Scientific data | Immutable raw capture, validated records, EDM objects and derived physics/engineering products. |
| Sensor/telemetry | Continuous operating measurements and pose, archived and resolved into time-dependent conditions. |

DAQ participates in control and scientific acquisition. A shared service framework does not imply
that low-rate telemetry and raw detector traffic use the same transport. The three-plane model and
time/conditions boundary follow ADR-012 §9.

## 5. Scientific processing and data

```text
Live acquisition / recorded replay / synthetic acquisition
                         |
                 common raw-stream contract
                         |
      immutable raw persistence + decode/unpack/validation
                         |
              validated board-frame records
                         |
              event building and reconstruction
                         |
          hits / clusters / tracks -> physics products
                         |
        angular distributions -> density inversion -> engineering products
```

Preprocess validates transport records, including CRC and malformed/lost-frame handling. Recon
owns event assembly from validated fragments and subsequent physical reconstruction. Detailed
ordering, calibration and clustering are component-specific; the diagram is not an acceptance
specification for algorithms or a fixed host event format.

Reconstruction is an internal configurable DAG, initially using Taskflow. Online and offline use
the same library targets. Algorithms consume EDM objects and immutable conditions, not files,
USB handles, mutable configuration branches or live telemetry. Keep serialization and persistence
outside algorithm logic and avoid private side channels or hidden global state.
Rationale: [ADR-001](../adr/ADR-001_reconstruction_runtime.md) and
[ADR-002](../adr/ADR-002_muon_edm_serialization.md).

| Data layer | Responsibility |
|---|---|
| Raw capture | Byte-preserving, immutable and reproducible input with acquisition metadata; processing never overwrites it. |
| Muon EDM | Canonical scientific vocabulary: events, raw hits, hits, clusters, tracks and conditions. Concrete schemas follow component contracts. |
| Derived products | Tracks, hit maps, rates, flux/angular distributions, opacity/density estimates and associated quality/uncertainty information. |
| Analytics and applications | Structured products for studies, reporting and visualization; Arrow/Parquet is the current storage direction, not the raw-capture container decision. |

## 6. Conditions, time and provenance

Conditions combine static detector/model information, assembly/deployment geometry and alignment,
calibration, and time-dependent measurements. Online providers and offline builders resolve these
into compatible immutable snapshots. Core owns schemas and interpretation; payload ownership is
specified in the repository model and [core conditions guidance](../../../core/docs/conditions.md).

The edge appliance is the common time authority, recording monotonic time with `boot_id` and UTC,
clock source and synchronization state. Domain controllers do not share a common clock. Map device
clocks to edge time using correlation records with uncertainty; do not equate detector timestamp
precision with global time accuracy. ADR-012 §9 gives an approximate 1 s common-time budget; exact
contract and device timestamp semantics remain in the owning specifications.

Every scientific product retains instrument/hardware and firmware identity, software/core revision,
algorithm version/parameters, geometry/calibration and conditions snapshot identity/hash, and time.
Raw provenance and selected conditions must permit reproducible reprocessing. An explicit conditions
override retains both original and replacement identities. Source decisions: ADR-002, ADR-012 §9–§10
and [ADR-004](../adr/ADR-004_deployment_update_strategy.md).

## 7. Replay, simulation and digital twin

Reconstruction is independent of acquisition origin. Recorded replay and synthetic acquisition
provide the same downstream raw-stream contract as live acquisition. Replay supports algorithm
iteration, regression, demonstrations and dataset generation. Fidelity includes timing, ordering,
trigger structure, metadata and configurable rates/loss injection as specified by the replay component.
Raw archives remain immutable; versioned validation fixtures follow
[ADR-011](../adr/ADR-011_test_data.md).

Simulation connects geometry and density models to muon generation, detector response and DAQ-format
output. Compare reconstruction with synthetic truth and recorded references using documented
metrics/tolerances such as efficiency, angular resolution, throughput and latency. Simulation does
not replace hardware acceptance. Rationale: [ADR-008](../adr/ADR-008_simulation_verification_replay.md).

The digital twin connects physical-object geometry, detector deployment/acceptance, measurement
products, density fields and engineering interpretation. Keep geometry independent of visualization
code and retain consistent model identities across simulation, reconstruction and display. Sources
may include CAD/BIM, surveys or geological models; candidate geometry tools include FreeCAD,
OpenSCAD and Blender. These are options, not mandatory runtime dependencies.
Rationale: [ADR-007](../adr/ADR-007_digital_twin_strategy.md).

## 8. Deployment and technology direction

Development targets Linux x86_64; deployment includes Linux desktops and ARM64 edge appliances.
Use systemd service lifecycle management and Debian packages initially. RAUC/Mender-style atomic
OTA and fleet management are production roadmap items, not implemented capabilities. Preserve
ARM64 compatibility, reproducible release identity and offline deployment needs. ADR-004 describes
versioning across hardware, firmware, software, algorithms and calibration; the repository model
identifies instrument release manifests/BOMs.

| Area | Direction and qualification |
|---|---|
| Firmware | Zephyr RTOS on MCU controllers, with STM32 a candidate platform; FPGA handles detector-specific processing. |
| Scientific software | C++, CMake, Muon EDM and Taskflow. Language standard and dependency tooling follow component build/spec requirements; see §10. |
| Service communication | Protobuf/gRPC preferred; optional Zenoh/ZeroMQ must have a justified use. Physical bus/transport specifications remain separate. |
| Dependencies | Conan or vcpkg are candidate package-management directions; no requirement to adopt both. |
| Analytics | Arrow/Parquet; raw transport and capture formats are separate contracts. |
| Visualization | Qt/QML, VTK and ParaView; operator access may be remote/headless or local according to deployment. |
| Simulation | Geant4 plus fast simulation and detector-response models. |

This table consolidates existing direction, not approval to add every dependency. Select technologies
for the actual problem, maintainability and ARM64 support. Workspace and agent procedures live in the
[developer guide](../workflow/DEVELOPER_GUIDE.md) and [session scope protocol](../../work/README.md).

## 9. Reliability and verification

Key concerns are HV/gas protection, DAQ integrity, unattended operation, watchdog recovery, fault
reporting, remote diagnostics and safe shutdown. Keep deterministic safety behavior local to domain
controllers; orchestration does not substitute for local protection.

Trace requirements to unit/contract tests, replay/golden comparisons, simulation validation and
hardware-in-loop acceptance as appropriate. Reference requirement IDs and preserve golden inputs.
Report missing datasets, incomplete interfaces and hardware checks not performed. A successful
software build or replay is not evidence of verified detector behavior.

## 10. Open points and document discrepancies

These are preserved questions, not decisions introduced by consolidation:

| Topic | Evidence / required resolution |
|---|---|
| Slow-control bus topology | Four sources differ: the [instrument architecture guide](../guide/instrument_architecture.md) describes three RS-485/Modbus buses (apparently current hardware); the management bus specification proposes one RS-485 bus with COBS/protobuf; ADR-005 §5–§6 evaluates Modbus for gas/auxiliary sensors and CAN-FD for distributed control; engineering context describes eventual CAN-FD, and SRD §10 lists all options. Record current hardware, baseline target and future evolution separately, with migration scope and compatibility, before implementing. |
| DAQ management on the shared bus | The bus diagram includes a DAQ node, while engineering context emphasizes a separate high-rate DAQ link. Separate management participation from raw transport and confirm the intended topology. |
| Motion-control boundary | Engineering context and SRD §6.4 combine pose sensing with future motion control. Pose measurement is established; decide ownership and safety/interfaces for future active actuation. |
| HV numerical targets | [SRD §6.2](../requirements/SRD.md) gives 0–2000 V and sub-nanoamp current measurement as an “Example target”, not an acceptance requirement. Confirm them against HV hardware evidence and assign HV requirement IDs before using them as acceptance limits. |
| C++ standard | Earlier system text named C++20; general guidance says C++, and the developer guide lists a C++17 toolchain. Component specifications/builds govern today; record an explicit requirement before imposing a workspace-wide standard. |
| DAQ formats and timestamps | Raw-capture container/provenance and device timestamp questions remain in the [DAQ proposal](../../changes/2026-10-daq-iteration-1/proposal.md). Do not infer answers from schematic “event” diagrams in older ADRs. |

Update this architecture and relevant component specifications when these points are decided, and
record consequential choices in an ADR. Planned services, telemetry/time contracts and later processing
modules must not be mistaken for completed implementations; inspect their owning specifications.
