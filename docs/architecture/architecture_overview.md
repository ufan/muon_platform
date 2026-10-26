# Architecture overview: scientific data chain

Living map of the scientific modules and the contracts between them, updated at step 0 of every
domain iteration ([engineering process §1](../workflow/engineering_process.md#1-development-approach)). Whole-system design: [system architecture](system_architecture.md).

## 1. Chain

```text
 detector ──USB/FX3──▶ daq ──raw stream──▶ preprocess ──board frames──▶ recon ──events/hits/tracks──▶ imaging
                        │                  (decode, CRC,               (event building,               (rates, flux,
                        │                   validation)                 hits, tracking)                opacity)
                        └──▶ raw persistence (immutable)                       └──▶ analysis
 replay ──same raw-stream contract──▶ preprocess …
```

Density inversion and other application products are a separate layer downstream of imaging
(§2). daq, preprocess and recon are modules of `core`; the arrows are contracts in `core/contracts/science/`.
The device ↔ host wire protocol belongs to the DAQ hardware reference (`core/daq/ref/<target>/`).

| Module | Responsibility |
|---|---|
| daq | Command acquisition hardware; produce raw bytes and run metadata. |
| preprocess | Decode raw frames into validated board records (framing, CRC, malformed or lost frames). |
| recon | Build events and reconstruct hits, clusters and tracks from validated records and conditions. |
| imaging | Compute physics products from tracks: rates, angular flux, opacity. |
| analysis | Validate, calibrate and study outputs. |
| conditions | Resolve geometry, mapping, alignment, calibration and telemetry intervals into immutable snapshots. |

## 2. Processing stages

The chain falls into three stages by purpose. Stages group modules; they are not modules.

| Stage | Content | Modules | Role |
|---|---|---|---|
| Event reconstruction | raw data → decoded records → events, hits, clusters, tracks | daq, preprocess, recon | mandatory; common to every application |
| Physics products | muography quantities: rates, angular flux, opacity | imaging | mandatory; the minimum value, common to every application |
| Application products | use-case products: density models, anomaly maps, risk indicators, reports | application layer, outside the scientific chain | value-added; may fuse other data (geology, BIM, surveys, telemetry) |

Event reconstruction and physics products run online and offline on shared code.

## 3. Downstream needs

Checked before an upstream contract is frozen.

| Contract | Consumers | Known needs | Open |
|---|---|---|---|
| Raw stream (daq → preprocess) | preprocess, persistence, replay | byte-exact capture, run metadata, loss markers | chunking for several, possibly disconnected consumers |
| Board frames (preprocess → recon) | event builder | event key, source/chip/channel identity, timestamps, validation flags ([draft](../../../core/contracts/science/pipeline/README.md)) | late, duplicate and timeout policy |
| Event frames (recon → downstream) | hit building, monitoring, persistence | status and reason, source coverage, host timestamps | schema, per-consumer payload |
| Tracks (recon → imaging, analysis) | imaging, analysis | direction, reference-plane position, fit quality, time | uncertainty model, selection flags |

## 4. Boundary test for a new module

Is it about bytes, records, events, tracks, studies or images? Does it produce or
consume a canonical contract? Can it run online, or only offline? If it spans more than one layer,
the boundary is too wide.
