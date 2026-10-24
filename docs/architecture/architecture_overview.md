# System Architecture Overview

Status: current; living document, updated at step 0 of every domain iteration (ADR-010).
Detailed whole-system design: [system architecture](system_architecture.md).
Repository boundaries/dependencies: [repository model](repository_model.md).
Document scopes and rationale links: [architecture index](readme.md).

This map is intentionally coarse: it describes technical responsibilities, data flow and downstream
needs. Detailed specifications are developed within each domain. Active iterations and task state
are discovered through the [work index](../../work/index.yml) and its linked records.

## 1. Data-plane chain

```text
 detector ──USB/FX3──▶ daq ──raw stream──▶ preprocess ──decoded board frames──▶ recon ──events/hits/tracks──▶ imaging
   (hw)               (bytes +             (decode, CRC,                        (event build,                  (opacity,
                       run metadata)        validation)                          hits, tracking)                 inversion)
                          │                                                          │
                          └──▶ raw persistence (immutable)                           └──▶ analysis (validation, flux, calibration)

 replay / simulation ──same raw stream contract──▶ preprocess …   (ADR-008)
```

daq, preprocess and recon are modules of one repository, `core` (ADR-012). The arrows between them are
scientific contracts in `core/contracts/science/`. The detector ↔ daq link (device ↔ host wire protocol) is
owned by the DAQ hardware references in `core/daq/ref/<target>/`. Sensor domains feed reconstruction only
through conditions (ADR-012 §9).

## 2. Domains and responsibilities

| Domain | Responsibility |
|---|---|
| contracts | Canonical scientific formats and shared domain-service interfaces; ownership is in the repository model. |
| daq | Command acquisition hardware and produce bytes plus run metadata. |
| preprocess | Decode raw frames into validated board records; keep transport validation separate from physical event building. |
| recon | Assemble events and reconstruct hits, clusters and tracks from validated records and conditions. |
| imaging | Convert tracks/flux into opacity or density products. |
| analysis | Validate, calibrate and study scientific outputs. |
| simulation | Generate synthetic truth, detector responses and DAQ-compatible inputs. |
| conditions | Resolve geometry, mapping, alignment, calibration and telemetry-derived intervals into immutable snapshots. |
| sensor domains | HV, gas, environment, pose and LV services isolate hardware control and telemetry. |
| instrument | Coordinate domains, operating modes, interlocks and external access. |
| applications | Operator interfaces, visualization, engineering interpretation and reporting. |

Repository maturity comes from manifests/metadata (`muon list`); component implementation status
comes from its specifications. Architectural roles here are not a claim that all domains exist.

## 3. Three information planes

- **Control**: commands, lifecycle, configuration, health and safety through instrument/domain services.
- **Scientific data**: raw capture → validated records → EDM objects → products; algorithms use an
  internal dataflow pipeline, not a microservice mesh.
- **Sensor/telemetry**: archived operating measurements resolved into conditions before reaching
  scientific algorithms. See [system architecture](system_architecture.md#4-three-information-planes).

DAQ combines a control-plane state machine with a scientific raw-stream producer.

## 4. Downstream needs (checked before freezing an upstream contract)

| Contract | Consumer | Known needs | Open questions |
|---|---|---|---|
| raw stream (daq → preprocess) | preprocess, persistence, replay | byte-exact capture; run/session metadata; loss detection markers | chunking and framing for multiple, possibly disconnected consumers |
| decoded board frames (preprocess → recon) | recon | `trigger_id`, board/chip/channel identity, timestamps, quality flags | timeout and coverage semantics for incomplete events |
| tracks (recon → imaging/analysis) | imaging, analysis | direction, position at reference plane, fit quality, time | uncertainty model; selection flags |

## 5. Boundary questions for any new module

Is it about bytes, records, events, tracks, studies, images or simulated
truth? Does it produce or consume a canonical contract? Could it run
online, or only offline? If the answer spans more than one layer, the
boundary is too wide.
