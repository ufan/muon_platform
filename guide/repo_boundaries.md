# Sharper Repo Boundary Proposal

## Why sharpen the split

The current workspace already points toward a multi-repo layout, but the actual contents still blur three different concerns:

- online acquisition and transport handling
- event-domain reconstruction
- offline analysis and experiment-specific outputs

The blur is most visible in `preprocess/`, which currently mixes byte-stream decode, event-oriented transforms, and detector-specific utilities, and in `analysis/`, which mixes reusable logic, notebooks, plots, and committed datasets.

The sharper split below keeps the existing domain names, but makes each repository responsible for one runtime layer and one kind of artifact.

## Boundary rule

Each top-level repository should answer exactly one question:

- `protocol/`: what are the shared wire, file, and data contracts?
- `daq/`: how does hardware get commanded and how do bytes leave the detector?
- `preprocess/`: how are raw transport frames decoded into validated board-level records in real time?
- `recon/`: how are decoded records assembled into physical events, hits, and tracks?
- `analysis/`: how are reconstructed outputs validated, calibrated, and studied offline?
- `imaging/`: how are reconstructed tracks converted into opacity or imaging products?
- `simulation/`: how are synthetic events, detector responses, and acceptance studies generated?
- `config/`: what detector/site configuration and calibration data parameterize the other repos?
- `tools/`: what small developer or operator utilities exist outside the core runtime pipelines?
- `archive/`: what legacy implementations are retained only as behavioral references?

If a module cannot be assigned to one of those questions cleanly, it is crossing a boundary and should be split.

## Proposed dependency graph

Allowed high-level dependencies:

- `config` -> no runtime dependency on other domain repos
- `protocol` -> may reference schemas and example fixtures only
- `daq` -> depends on `protocol`, reads `config`
- `preprocess` -> depends on `protocol`, reads `config`
- `recon` -> depends on `protocol`, reads `config`
- `analysis` -> depends on `protocol`, `recon` output schemas, reads `config`
- `imaging` -> depends on `protocol`, `recon` output schemas, reads `config`
- `simulation` -> depends on `protocol`, reads `config`
- `tools` -> may depend on stable public interfaces from other repos, but must not define canonical data models

Disallowed dependencies:

- `protocol` importing implementation code from any other repo
- `daq` containing event building, tracking, imaging, or physics analysis
- `preprocess` containing track finding, detector alignment, or final reconstruction products
- `analysis` becoming the source of truth for production data formats
- `imaging` reaching back into raw byte decode
- `config` embedding executable pipeline logic

## Contract objects at the boundaries

The split should be enforced by concrete handoff objects rather than by directory names alone.

### 1. `protocol/`

Owns the canonical definitions for:

- command/status wire protocol
- USB/ADM/chip frame layout
- device state model
- stable file schemas for handoff artifacts
- event and hit vocabulary

Recommended sub-boundaries inside `protocol/`:

- `protocol/wire/`: host-device command and stream framing
- `protocol/pipeline/`: schemas for decoded frames, built events, hits, tracks, summaries
- `protocol/persistence/`: ROOT/Parquet/JSON metadata conventions and dataset manifests
- `protocol/db/`: only if database schemas become real and shared

`protocol/` should not contain DAQ control code or reconstruction algorithms.

### 2. `daq/`

Owns:

- hardware discovery and device session lifecycle
- command transmission and status handling
- acquisition mode control
- transport adapters such as FX3/USB readers
- online process supervision and operator-facing acquisition services

Inputs:

- wire protocol definitions from `protocol/`
- detector/site settings from `config/`

Outputs:

- raw transport byte streams
- command/status logs
- run/session metadata

`daq/` should stop at bytes plus operational metadata. It should not define host-side events.

### 3. `preprocess/`

Owns:

- streaming decode of raw bytes into validated USB/ADM/chip records
- CRC and frame-structure validation
- loss detection, malformed-frame quarantine, and stream health metrics
- optional lightweight normalization that is still transport-adjacent

Inputs:

- raw DAQ stream
- `protocol/wire` schema
- board/channel mapping from `config` when required for structural decoding

Outputs:

- decoded board-frame records
- bad-frame side channel
- online counters and quality summaries

`preprocess/` should not aggregate by `trigger_id` into full events. That belongs in `recon/`.

### 4. `recon/`

Owns:

- event building keyed by `trigger_id`
- timeout/coverage handling for incomplete events
- conversion from chip/board payloads into detector hits
- geometry-aware hit positioning
- track reconstruction and fit products
- reconstruction quality flags

Inputs:

- decoded frame records from `preprocess/`
- geometry, alignment, mapping, and calibration from `config/`
- event/hit/track schemas from `protocol/pipeline`

Outputs:

- built events
- hit collections
- track collections
- reconstruction diagnostics

This is the missing boundary that the current repo needs most. Several things now living in `preprocess/src/` appear to belong here.

### 5. `analysis/`

Owns:

- offline validation and performance studies
- calibration derivation workflows
- plotting, notebooks, and experiment-specific studies
- comparative checks between runs, detector setups, and reconstruction versions

Inputs:

- stable outputs from `recon/`
- `config/`
- optional simulation truth from `simulation/`

Outputs:

- reports, figures, notebooks, calibration candidates, QA summaries

`analysis/` should be consumer-only with respect to production reconstruction outputs.

### 6. `imaging/`

Owns:

- opacity calculations
- inversion and density reconstruction
- geology/site-model ingestion specific to imaging
- imaging-specific visualization products

Inputs:

- reconstructed tracks from `recon/`
- site geometry/material models from `config/` or imaging-owned inputs

Outputs:

- opacity maps
- inversion products
- 2D/3D imaging artifacts

`imaging/` should not need to know anything about USB framing or DAQ session control.

### 7. `simulation/`

Owns:

- event generators
- detector response simulation
- acceptance estimation
- synthetic benchmark datasets

Inputs:

- detector geometry/configuration
- protocol/pipeline schemas when producing comparable synthetic outputs

Outputs:

- truth events
- simulated detector hits or tracks
- benchmark datasets for recon/analysis/imaging

### 8. `config/`

Owns only data and schemas for:

- detector geometry
- link/channel mapping
- alignment and rotation
- z positions
- site-specific deployment configuration
- calibration constants and versioned overrides

Recommended rule: `config/` is versioned data, not code, except for minimal schema validation helpers.

## What should move where from the current tree

### Keep in `protocol/`

- `protocol/wire/doc/formal_protocol_spec.md`
- `protocol/wire/daq.asn`
- device state documentation

### Keep in `config/`

- site folders such as `config/150test/`, `config/400test/`, `config/liaoda/`, `config/nankeda/`, `config/shentie/`

### Keep in `simulation/`

- `simulation/EcoMug-2.1/`
- `tools/rate_estimate/` is simulation-adjacent and could remain a tool or later move under `simulation/tools/`

### Move out of `preprocess/` over time

Move to `daq/`:

- `preprocess/src/fx3/`
  This is a transport adapter and acquisition boundary, not preprocessing.

Move to `recon/`:

- `preprocess/src/hit_position_reconstruct/`
- `preprocess/src/track_seek/`
- likely parts of `preprocess/src/adas_muxbrd_fit/` if they operate on built hits/tracks rather than raw frame decode

Keep in `preprocess/`:

- `preprocess/src/adas_data_decode/`
- `preprocess/src/adas_data_unpack/`
- `preprocess/src/usb_data_separate/`

Those names still need tightening, but they are closest to the raw-stream boundary.

### Split `analysis/` internally

The current `analysis/` tree mixes:

- source notebooks
- generated plots
- committed ROOT files
- helper code
- local experiment configs

At minimum, make the boundary visible:

- `analysis/notebooks/`
- `analysis/scripts/`
- `analysis/reports/`
- `analysis/fixtures/` for tiny checked-in examples only

Large generated files and local outputs should not be the normal committed interface for the repo.

## Recommended repository set

If this workspace is split into separate repositories, use this set first:

- `muon-protocol`
- `muon-config`
- `muon-daq`
- `muon-preprocess`
- `muon-recon`
- `muon-analysis`
- `muon-imaging`
- `muon-simulation`
- `muon-tools`
- `muon-archive` or per-legacy archived repos

Do not create more repos yet. In particular, avoid splitting by detector site, algorithm, or file format before the `recon` boundary is stable.

## First migration steps

1. Freeze the handoff between `preprocess` and `recon`.
   Define a schema for "decoded board-frame record" in `protocol/pipeline/`.

2. Create `recon/` as an interface-first skeleton.
   Start with event builder, hit model, and track model contracts, even if the implementation is thin.

3. Move `fx3` ownership to `daq/`.
   Treat hardware readout as acquisition, not preprocessing.

4. Reclassify current `preprocess/src/*`.
   Keep only transport-adjacent decode modules in `preprocess/`.

5. Make `analysis/` a consumer.
   It should read stable `recon` outputs instead of acting as an informal reconstruction layer.

6. Keep `archive/` read-only.
   Legacy code should inform contracts and regression fixtures, not remain on the active dependency path.

## Decision test for future code

Before adding a new module, ask:

- Is this concerned with bytes, events, tracks, studies, images, or simulated truth?
- Is it producing a canonical contract or consuming one?
- Could this run online in the DAQ path, or only offline after event reconstruction?
- Would another subsystem need this as a stable interface, or is it a local utility?

If the answer spans more than one of those layers, the module boundary is still too wide.
