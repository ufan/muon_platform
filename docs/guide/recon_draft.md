# Recon Draft

Status: proposed (input to the future recon iteration; not a decision). `recon/` is a planned module of `core`; contracts belong in `core/contracts/science/` per the [repository model](../architecture/repository_model.md) (earlier drafts used `protocol/pipeline`). Event-builder requirements already extracted to core are listed in [event_builder.md](event_builder.md).

## Purpose

`recon/` owns the event-domain pipeline after transport decode:

- event assembly from validated board fragments
- event-frame publication
- intermediate event-builder observability for debugging and monitoring
- hit building
- track reconstruction
- reconstruction diagnostics

For the current online design, the event builder should live inside `recon/` as a dedicated subdomain, not as a separate top-level repository.

## Proposed internal layout

```text
recon/
  README.md
  event_builder/
    README.md
    include/
      recon/event_builder/event_builder.hh
      recon/event_builder/event_frame.hh
      recon/event_builder/decoded_board_frame.hh
      recon/event_builder/completion_policy.hh
      recon/event_builder/publisher.hh
      recon/event_builder/metrics.hh
    src/
      event_builder.cc
      event_table.cc
      event_merge.cc
      completion_policy.cc
      publisher_router.cc
      metrics.cc
    tests/
      event_builder_smoke.cc
      timeout_flush.cc
      duplicate_fragment.cc
      partial_event_publish.cc
  hit_builder/
    README.md
    include/
      recon/hit_builder/hit_builder.hh
      recon/hit_builder/hit_collection.hh
    src/
      hit_builder.cc
  tracking/
    README.md
    include/
      recon/tracking/track_finder.hh
      recon/tracking/track_collection.hh
    src/
      track_finder.cc
  apps/
    online_recon_main.cc
  fixtures/
    decoded_fragments/
    events/
```

The names can change, but the ownership split should stay:

- `event_builder/` owns assembly of logical events
- `hit_builder/` consumes finalized event frames
- `tracking/` consumes hit collections
- `apps/` wires runtime processes together

## Why this should stay inside `recon/`

The event builder is the first reconstruction-stage component. It already operates on decoded detector contributions and produces logical event frames, which are reconstruction-domain objects rather than transport-domain objects.

Keeping it in `recon/` avoids two bad outcomes:

- `preprocess/` growing upward into event semantics
- a tiny standalone repo whose only job is one narrow stage in the reconstruction pipeline

## Module responsibilities

### `event_builder/decoded_board_frame`

Input contract received from `preprocess/`.

Owns only the reconstruction-facing view of a validated board contribution:

- run identity
- stream or device identity
- `trigger_id`
- `adm_index`
- sync metadata
- decoded chip payloads
- validation and warning flags
- host receive timestamp

This type should be defined against the scientific contracts in `core/contracts/science/`, with a local adapter only if needed.

### `event_builder/event_frame`

Canonical published output of the event builder.

Should contain:

- event identity
- received board contributions
- coverage masks
- completion status
- host lifecycle timestamps
- corruption and duplicate flags
- completion reason

This is the handoff object for:

- monitoring
- persistence
- hit building
- fast QC

### `event_builder/event_builder`

Public orchestration interface for the module.

Recommended surface:

```text
push(decoded_board_frame)
poll_expired(now)
flush(run_id)
subscribe(publisher)
```

Responsibilities:

- own event table lifecycle
- merge fragments by `trigger_id`
- apply completion policy
- finalize event frames
- publish finalized results
- expose optional intermediate observers for metrics and lifecycle state

### `event_builder/event_table`

In-memory state for in-progress events.

Each active entry should track:

- event key: `run_id`, `trigger_id`
- expected board coverage
- received board fragments keyed by `adm_index`
- duplicate/conflict bookkeeping
- timeout deadline
- event health flags
- first/last-seen timestamps

This state should stay private to the event builder implementation.

### `event_builder/event_merge`

Pure merge logic for combining one decoded board fragment into an in-progress event entry.

It should decide:

- first fragment vs duplicate
- accepted replacement vs rejected replacement
- coverage mask update
- warning propagation

Keeping this separate makes it easier to test deterministic merge behavior without bringing up the full runtime.

### `event_builder/completion_policy`

Rules for deciding when to publish an event.

It should support at least:

- complete by expected board coverage
- partial by timeout
- partial by fatal corruption policy

Configuration inputs should include:

- required board mask
- timeout budget
- duplicate replacement policy
- corruption tolerance policy

### `event_builder/publisher`

Abstract downstream sink interface.

Recommended minimal contract:

```text
publish(event_frame) -> publish_result
```

Expected implementations:

- in-process callback publisher
- queue/socket publisher
- file sink
- metrics or monitor sink

The core event builder should not know transport details of these sinks.

This final publisher interface should coexist with intermediate observer hooks for:

- decoded-fragment visibility
- event-table metrics
- event lifecycle notifications

### `event_builder/publisher_router`

Fan-out adapter that sends one finalized event frame to multiple publishers.

This is the right place for:

- per-sink success/failure accounting
- best-effort vs fail-fast behavior
- retry or drop bookkeeping

### `event_builder/metrics`

Small, explicit accounting surface for online operation.

At minimum track:

- fragments received
- events completed
- events timed out
- duplicate fragments
- corrupt fragments
- publish failures

## Online runtime flow

The intended runtime wiring is:

```text
DAQ
-> preprocess decode
-> decoded_board_frame
-> recon::event_builder
-> event_frame
-> publishers
-> hit_builder
-> tracking
```

Optional observers may attach at:

- `decoded_board_frame`
- event-builder metrics
- event lifecycle notifications
- finalized `event_frame`

Important boundary rule:

- `preprocess/` never publishes full event frames
- `event_builder/` never parses raw USB bytes

## Minimal interfaces to define first

If implementation starts now, define these first:

1. `decoded_board_frame` contract (`core/contracts/science/`)
2. `event_frame` contract (`core/contracts/science/`)
3. `recon/event_builder/event_builder.hh`
4. `recon/event_builder/completion_policy.hh`
5. `recon/event_builder/publisher.hh`

That is enough to let `preprocess/` and downstream consumers build against stable seams before all algorithms exist.

## Recommended first implementation scope

Keep the first version narrow:

- single-process runtime
- in-memory event table
- coverage and timeout completion
- one in-process publisher
- fixtures for complete, partial, duplicate, and corrupt fragment cases

Do not couple the first implementation to:

- database persistence
- UI transport
- imaging logic
- full tracking

## Migration guidance from the current tree

As code moves out of `preprocess/src/`, the likely order is:

1. keep raw decode components in `preprocess/`
2. introduce `recon/event_builder/`
3. move hit-position logic into `recon/hit_builder/`
4. move track search logic into `recon/tracking/`

That keeps the boundary sharp while still allowing incremental migration.
