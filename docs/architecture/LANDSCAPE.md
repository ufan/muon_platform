# Platform Landscape (coarse map)

Status: living document. Updated at step 0 of every domain iteration (ADR-010).
Detailed boundary rationale: [guide/repo_boundaries.md](../guide/repo_boundaries.md).
Repository baseline and workspace model: [ADR-012](../adr/ADR-012_repository_baseline_and_workflow.md).

This map is intentionally coarse. Only the domain currently in its iteration
gets detailed specs. Everything else is described just well enough to keep
its boundary and downstream needs visible.

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

## 2. Domains and current state

| Domain | Answers | Project | Maturity | Iteration |
|---|---|---|---|---|
| contracts | Scientific contracts (`core/contracts/science`); system contracts staged in `core/contracts/system`, later `muon_contracts` | `core`, `contracts` (placeholder) | incubating | with each domain |
| daq | How is hardware commanded, and how do bytes leave the detector? | `core/daq` | active | **1 (now)** |
| preprocess | How are raw frames decoded into validated board-level records? | `core/preprocess` (planned; legacy in `legacy/muon400_process`) | legacy | 2 |
| recon | How are records assembled into events, hits and tracks? | `core/recon` (planned; draft: [guide/recon_draft.md](../guide/recon_draft.md)) | planned | 3 |
| imaging | How are tracks turned into opacity/density products? | — (host-local archive `archive/imaging`; development approach undecided) | planned | 4 |
| analysis | How are outputs validated, calibrated and studied offline? | — (legacy in `legacy/analysis`) | legacy | 4 |
| simulation | How are synthetic events and detector responses generated? | — | planned | as needed |
| conditions | Geometry, mapping, alignment, calibration, telemetry-derived intervals | interpretation in `core`; payloads in `config` (support) | support | with preprocess |
| sensor domains | HV, gas, environment, pose, LV: one repository each (firmware + service) | — | planned | after DAQ |
| instrument | coordination, operating modes, product profiles, BOM | `muon_instrument` (future) | planned | after the first sensor domain |
| firmware | FPGA / MCU | — | planned | — |
| ux | CLI / TUI / GUI / web adapters | — | planned | — |

## 3. Control plane vs data plane

- **Control plane**: device state, commands, configuration, health, safety.
  Covers DAQ control, HV, gas, pose and the central instrument manager. Service
  contracts are protobuf/gRPC (see `AGENTS.md` technology direction).
- **Data plane**: raw stream → EDM objects → products. It is an in-process
  dataflow pipeline, not a microservice mesh.

DAQ sits on both planes: a control-plane state machine and a data-plane
raw-stream producer.

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
