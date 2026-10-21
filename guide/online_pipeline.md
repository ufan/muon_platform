# Online Data Pipeline

## Purpose

This guide defines one shared online data pipeline for two operating modes:

- real-time data acquisition from live hardware
- offline replay service from recorded raw data

The core rule is:

- same decode path
- same event-builder path
- same event-frame contract
- different ingress adapters
- optional observability taps at intermediate stages

This avoids building one architecture for live DAQ and another for replay.

## Scope

This guide covers the path from raw input bytes to published event frames, including optional real-time consumers attached to intermediate pipeline outputs:

```text
source adapter
-> raw byte stream
-> preprocess decode and validation
-> decoded_board_frame
-> recon/event_builder
-> event_frame
-> downstream consumers
```

It does not define later hit-building, tracking, imaging, or analysis algorithms in detail.

## Operating modes

### Live mode

Live mode is the real-time acquisition path.

Ingress source:

- hardware device session
- USB or FX3 transport
- DAQ run control

Typical properties:

- wall-clock constrained
- backpressure matters
- fragment arrival order may vary
- device and host timing both matter

### Replay mode

Replay mode is the offline service path that replays previously recorded raw data through the same decode and event assembly pipeline.

Ingress source:

- recorded byte stream files
- raw packet logs
- archived DAQ fragments

Typical properties:

- pacing can be preserved or accelerated
- no live hardware dependency
- used for debugging, regression, benchmarking, or service replay

## Shared architecture

Both modes should use the same core pipeline:

```text
live_source | replay_source
-> raw_stream_adapter
-> preprocess
-> decoded_board_frame
-> recon/event_builder
-> publisher_router
-> consumers
```

Only the source adapter and runtime policy should vary by mode.

Debug and observability consumers may subscribe at intermediate stages such as:

- raw stream input
- `decoded_board_frame`
- in-progress event-builder metrics
- finalized `event_frame`

## Domain ownership

### `daq/`

Owns source adapters that produce raw byte streams.

Live-side responsibilities:

- device discovery
- session start/stop
- command/status handling
- USB or FX3 readout
- run metadata

Replay-side responsibilities may live here or under `tools/`, but they should expose the same source interface:

- open recorded raw stream
- read chunks or packets
- emit raw byte stream into the pipeline

### `preprocess/`

Owns the shared decode stage for both live and replay modes.

Responsibilities:

- detect frame boundaries
- decode USB/ADM/chip structures
- validate CRC and structure
- emit validated board-level fragments
- emit malformed-fragment diagnostics
- expose real-time metrics and optional debug consumers on intermediate decode outputs

`preprocess/` must not know whether bytes came from a live detector or a replay file, except for optional metadata tagging.

### `recon/`

Owns the shared event-domain path for both live and replay modes.

Responsibilities:

- aggregate validated fragments by `trigger_id`
- apply completion and timeout policy
- finalize event frames
- publish event frames to downstream consumers
- expose event-builder metrics and optional debug consumers for in-progress state transitions

`recon/` must not know whether decoded fragments originated from live transport or replay input, except for optional mode metadata.

## Canonical contracts

The pipeline should expose three major contract layers plus observability outputs.

### 1. Raw stream input

Produced by the source adapter.

Required properties:

- ordered byte chunks as observed by the source
- source metadata such as run, device, file, or stream id
- host-side observation timestamp

Optional fields:

- recorded timestamp from the original run
- source offset
- replay pacing metadata

### 2. `decoded_board_frame`

Produced by `preprocess/`.

This is the shared handoff object between transport decode and event-domain assembly.

Required contents:

- `run_id`
- `stream_id` or `device_id`
- `trigger_id`
- `adm_index`
- `frame_index`
- `dcm_sync_id`
- `adm_sync_id`
- detector timestamp if available
- decoded chip payloads
- validation state
- host receive timestamp

### 3. `event_frame`

Produced by `recon/event_builder/`.

This is the canonical output for downstream services.

Required contents:

- `run_id`
- `event_id`
- `trigger_id`
- `event_status`
- `expected_adm_mask`
- `received_adm_mask`
- `missing_adm_mask`
- `board_fragments`
- `host_first_seen_ts`
- `host_last_update_ts`
- `host_completed_ts`

### 4. Observability outputs

These are not replacements for the canonical contracts above. They are optional, real-time side outputs for debugging, monitoring, and hardware bring-up.

Recommended observable outputs:

- raw stream counters and chunk metadata
- decode-stage metrics
- `decoded_board_frame` debug stream
- malformed-fragment stream
- event-builder counters
- event lifecycle notifications such as created, updated, timed out, finalized

These outputs are especially important during hardware debugging, where engineers need live visibility into middle-stage outputs before final event assembly is stable.

## What must be identical across live and replay

The following semantics should not change by mode:

- USB/ADM/chip decode rules
- fragment validation rules
- event identity keyed by `trigger_id`
- board-coverage completion rules
- timeout-flush semantics at the event-builder level
- `decoded_board_frame` schema
- `event_frame` schema
- downstream publisher interface
- meaning of intermediate observability outputs when enabled

This is the core design constraint. Replay is not a special-case reconstruction path.

## What may differ across live and replay

These are valid mode-specific differences:

- source adapter implementation
- pacing policy
- clock policy
- backpressure policy
- sink selection
- operational observability

### Pacing policy

Live mode:

- paced by hardware arrival

Replay mode may support:

- original-time replay
- scaled-time replay
- maximum-throughput replay

Pacing policy should live at the source adapter, not inside `preprocess/` or `recon/`.

### Clock policy

Live mode should stamp:

- host receive timestamps from the current runtime clock

Replay mode may stamp:

- replay host time
- preserved recorded host time
- both, when useful

The chosen policy should be explicit in metadata. Do not silently overload one field with different meanings.

### Backpressure policy

Live mode may need:

- bounded queues
- drop or degrade behavior
- operator-visible pressure metrics

Replay mode can usually tolerate:

- pause and wait
- slower sinks
- deterministic re-run behavior

### Sink selection

Live mode may publish to:

- online monitor
- alerting
- hot storage
- rolling QC service

Replay mode may publish to:

- regression checker
- offline storage
- benchmark harness
- debugging subscriber

## Source adapter contract

To keep the core pipeline shared, define one source adapter interface for both modes.

Recommended behavior:

```text
open(source_config)
read() -> raw_stream_chunk
close()
```

Where `source_config` selects:

- live hardware session
- replay file or dataset
- pacing mode
- clock policy

The source adapter should not decode detector frames. It only emits raw bytes plus source metadata.

## Publisher contract

The shared downstream boundary should stay generic:

```text
publish(event_frame) -> publish_result
```

Publisher implementations can differ by mode, but the event-builder output should remain canonical.

Supported publisher classes:

- in-process subscriber
- message queue or socket sink
- file sink
- monitoring sink
- debug dump sink

The pipeline should also support subscribers before the final publisher stage.

Recommended stage-local subscription points:

- raw-stream observer
- preprocess decode observer
- malformed-fragment observer
- event-builder metrics observer
- final event-frame publisher

## Failure handling

Failure semantics should stay visible in both modes.

At minimum, track:

- malformed raw fragments
- decode failures
- duplicate board fragments
- timed-out events
- partial event publication
- sink publish failures

Replay mode is especially useful for reproducing live failures, so it must preserve enough metadata to replay:

- source offsets
- raw-fragment identity
- recorded timing when available

Hardware-debugging mode should additionally support live inspection of:

- raw chunk rates
- frame boundary detection results
- per-board decoded payload summaries
- duplicate and missing-board counters
- event timeout and finalize counters

## Minimal deployment shape

A practical first deployment can be one process with mode-selected ingress:

```text
muon_pipeline --mode live
muon_pipeline --mode replay --input run-42.raw
```

Internal structure:

- source adapter
- preprocess decoder
- event builder
- publisher router

That is sufficient before introducing separate services.

## Recommended repository layout impact

The shared pipeline suggests this ownership:

- `daq/`: live source adapters and run-control integration
- `tools/` or `daq/`: replay source adapter
- `preprocess/`: shared decode path
- `recon/event_builder/`: shared event assembly and event publication
- `protocol/pipeline/`: contract definitions for `decoded_board_frame` and `event_frame`

## Recommended next interfaces

To make this guide actionable, define these next:

1. `protocol/pipeline/raw_stream_chunk`
2. `protocol/pipeline/decoded_board_frame`
3. `protocol/pipeline/event_frame`
4. source adapter interface for live and replay
5. event publisher interface

## Design rule summary

The architecture should be:

- one pipeline
- two ingress modes
- one decode path
- one event-builder path
- observable middle-stage outputs
- many consumer adapters

If live and replay begin to diverge in decode rules or event-frame semantics, the boundary is wrong.
