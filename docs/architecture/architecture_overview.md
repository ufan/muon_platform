# Architecture overview: scientific data chain

Living map of the scientific modules and the contracts between them, updated at step 0 of every
domain iteration (ADR-010). Whole-system design: [system architecture](system_architecture.md).

## 1. Chain

```text
 detector ──USB/FX3──▶ daq ──raw stream──▶ preprocess ──board frames──▶ recon ──events/hits/tracks──▶ imaging
                        │                  (decode, CRC,               (event building,               (opacity,
                        │                   validation)                 hits, tracking)                inversion)
                        └──▶ raw persistence (immutable)                       └──▶ analysis
 replay ──same raw-stream contract──▶ preprocess …
```

daq, preprocess and recon are modules of `core`; the arrows are contracts in `core/contracts/science/`.
The device ↔ host wire protocol belongs to the DAQ hardware reference (`core/daq/ref/<target>/`).

| Module | Responsibility |
|---|---|
| daq | Command acquisition hardware; produce raw bytes and run metadata. |
| preprocess | Decode raw frames into validated board records (framing, CRC, malformed or lost frames). |
| recon | Build events and reconstruct hits, clusters and tracks from validated records and conditions. |
| imaging | Convert tracks and flux into opacity or density products. |
| analysis | Validate, calibrate and study outputs. |
| simulation | Synthetic truth, detector response and DAQ-format input. |
| conditions | Resolve geometry, mapping, alignment, calibration and telemetry intervals into immutable snapshots. |

## 2. Downstream needs

Checked before an upstream contract is frozen.

| Contract | Consumers | Known needs | Open |
|---|---|---|---|
| Raw stream (daq → preprocess) | preprocess, persistence, replay | byte-exact capture, run metadata, loss markers | chunking for several, possibly disconnected consumers |
| Board frames (preprocess → recon) | event builder | event key, source/chip/channel identity, timestamps, validation flags ([draft](../../../core/contracts/science/pipeline/README.md)) | late, duplicate and timeout policy |
| Event frames (recon → downstream) | hit building, monitoring, persistence | status and reason, source coverage, host timestamps | schema, per-consumer payload |
| Tracks (recon → imaging, analysis) | imaging, analysis | direction, reference-plane position, fit quality, time | uncertainty model, selection flags |

## 3. Boundary test for a new module

Is it about bytes, records, events, tracks, studies, images or simulated truth? Does it produce or
consume a canonical contract? Can it run online, or only offline? If it spans more than one layer,
the boundary is too wide.
