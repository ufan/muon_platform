# Online Event Builder

Status: proposed; partly superseded. Event identity, completion, host timestamps and acceptance evidence now live in core: [event builder requirements](../../../core/daq/doc/specs/event-builder.md) and the [FX3 profile](../../../core/daq/doc/specs/event-builder-fx3.md) (`daq:FR-012`, `daq:ADR-006`). The contract field lists, status vocabulary, publication, observability and failure-surfacing rules below are not yet migrated; migration is pending an event-builder placement decision. `protocol/pipeline` references are obsolete: scientific contracts belong in `core/contracts/science/` ([repository model](../architecture/repository_model.md)).

## Purpose

For online data acquisition, the event builder is the boundary component between:

- `preprocess/`, which decodes the raw DAQ stream into validated board-level records
- `recon/`, which assembles those records into logical event frames and publishes them to downstream consumers

The event builder must run on the live stream. It is not an offline batch collector.

## Placement in the repository split

Responsibilities are split as follows:

- `daq/`: device control, acquisition lifecycle, raw byte transport
- `preprocess/`: USB/ADM/chip frame decode, validation, stream health checks
- `recon/`: event assembly, completion policy, event-frame publication

This means:

- raw bytes are not input to `recon/`
- full event aggregation does not belong in `preprocess/`
- the canonical downstream handoff is the published event frame
- debug and monitoring consumers may still subscribe to intermediate outputs and metrics before final event publication

## Online pipeline

The intended online path is:

```text
DAQ byte stream
-> preprocess raw frame decoder
-> preprocess validated board-frame record
-> recon event builder
-> recon published event frame
-> downstream consumers
```

Typical downstream consumers may include:

- online monitoring
- persistence / event logging
- fast quality control
- hit building and track reconstruction stages
- trigger-rate or detector-health summaries
- optional imaging or alerting paths

Intermediate-stage consumers may also subscribe during hardware debugging, especially to:

- `decoded_board_frame` output
- malformed-fragment diagnostics
- event-builder counters
- event lifecycle notifications

## Boundary contract

### Input from `preprocess`

`preprocess` should emit a validated board-frame record for each decoded ADM contribution.

Minimum required fields:

- `run_id`
- `stream_id` or `device_id`
- `trigger_id`
- `adm_index`
- `frame_index`
- `dcm_sync_id`
- `adm_sync_id`
- detector-side timestamp if present in the transport frame
- decoded chip payloads
- validation flags
- host receive timestamp

Optional but useful fields:

- CRC result
- byte-offset or packet-offset in the raw stream
- malformed-fragment side-channel reference
- per-frame decode warnings

`preprocess` may discard invalid raw fragments from the main path, but it should expose enough diagnostics for the event builder to distinguish:

- missing data
- corrupted data
- out-of-order arrival
- duplicate board contributions

### Output from `recon`

`recon` should publish one event frame per logical trigger group.

Minimum event-frame fields:

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

Recommended fields:

- `sync_id_summary`
- detector timestamp summary
- duplicate-fragment count
- corruption flags inherited from fragment metadata
- completion reason
- downstream schema version

`event_status` should be explicit, for example:

- `complete`
- `partial_timeout`
- `partial_corrupt`
- `duplicate_conflict`

### Intermediate observability from `recon`

In addition to finalized event-frame publication, `recon` should expose optional real-time observability outputs.

Recommended outputs:

- in-progress event count
- timeout count
- duplicate-fragment count
- per-board coverage summaries
- event lifecycle notifications such as created, updated, completed, timed out

These side outputs are especially useful during hardware debugging and should not be treated as replacements for the canonical `event_frame`.

## Event identity

### Strict key

For host-side event assembly:

- `trigger_id` is the only strict event key

All decoded board fragments with the same `trigger_id` belong to the same logical event unless the run or stream context changes.

### Non-strict metadata

The following fields must be preserved but must not be used as hard merge criteria:

- `dcm_sync_id`
- `adm_sync_id`
- `frame_index`
- board arrival order
- host receive order

This matters because:

- USB frames from different ADM boards are not guaranteed to arrive in board order
- sync identifiers are important diagnostics, but the event identity is governed by `trigger_id`

## Event assembly model

Within `recon/`, the event builder should maintain an in-memory event table keyed by:

- `run_id`
- `trigger_id`

Each in-progress event entry should contain:

- event header and lifecycle timestamps
- expected board coverage for the current run configuration
- received board fragments indexed by `adm_index`
- duplicate/conflict bookkeeping
- timeout deadline
- health and quality flags

Recommended assembly flow:

1. Receive a validated board-frame record from `preprocess`.
2. Locate or create the in-progress event entry by `trigger_id`.
3. Merge the board contribution under its `adm_index`.
4. Update coverage masks, timestamps, and diagnostics.
5. Check completion policy.
6. If complete or expired, finalize the event frame and publish it.

## Completion policy

The event builder should support both of the following completion modes:

- completion by expected board coverage
- completion by timeout

### Coverage completion

An event is `complete` when:

- all required ADM boards for the run are present
- no fatal fragment corruption blocks publication

Required board coverage should come from run configuration, not hard-coded board counts.

### Timeout completion

An event should be flushed as partial when:

- the configured assembly timeout expires before expected coverage is reached

This is required for live systems so that one missing board does not stall the entire stream.

### Duplicate handling

If the same `trigger_id` and `adm_index` appear more than once:

- preserve the first accepted fragment
- record the duplicate
- optionally replace only if the policy explicitly prefers a later fragment with a better validation state

The replacement policy must be deterministic and documented.

## Publication interface

The event builder should publish finalized event frames to a generic downstream consumer interface rather than writing directly into one hard-coded sink.

It should also support optional debug observers on intermediate state and metrics.

Recommended publisher abstraction:

```text
publish(event_frame) -> ack / retry / drop policy
```

Supported consumer classes should include:

- in-process subscriber
- queue or socket publisher
- file or database sink
- monitoring / metrics sink

Supported intermediate observers should include:

- decode-output observer
- event metrics observer
- lifecycle notification observer
- debug dump observer

Required publisher properties:

- non-blocking or bounded-blocking behavior
- backpressure visibility
- publish result accounting
- ability to route complete and partial events alike

The event builder should not assume that every consumer needs the same payload richness. A practical design is:

- canonical full event frame from `recon/`
- stage-local debug outputs for engineering visibility
- thin adapters that transform it for specific consumers

## Timestamp requirements

Each event frame should carry host-generated timestamps with at least microsecond resolution.

Required timestamps:

- `host_first_seen_ts`: when the first fragment for the event reached the host
- `host_last_update_ts`: when the latest fragment was merged
- `host_completed_ts`: when the event was finalized for publication

If detector timestamps are present, keep them separate from host timestamps. They serve different purposes:

- detector timestamp: detector-side timing context
- host timestamps: operational latency and event-builder timing

## Failure handling

The event builder must not silently lose ambiguity.

At minimum it should surface:

- missing board fragments
- invalid or corrupted board fragments
- duplicate board contributions
- impossible state transitions
- publish failures

Recommended behavior:

- emit partial events instead of holding them forever
- attach reason codes to incomplete publication
- maintain counters for timeout, corruption, duplicate, and publish-failure cases

## Minimal component split

The minimal implementation split should be:

### In `preprocess/`

- stream reader input adapter
- USB frame decoder
- ADM frame decoder
- chip frame decoder
- decode validation and fragment emission

### In `recon/`

- event table
- event merge logic
- completion policy
- event-frame schema
- publisher interface

This is the narrowest clean boundary for online acquisition without mixing transport decode with event-domain assembly.

## Recommended next interfaces

To make this design executable, define these contracts next:

1. `protocol/pipeline/decoded_board_frame`
2. `protocol/pipeline/event_frame`
3. `recon/event_builder` interface
4. `recon/event_publisher` interface

The first implementation can stay simple as long as the boundary stays strict:

- `preprocess` emits validated board-frame records
- `recon` owns all `trigger_id` aggregation
- downstream consumers see only published event frames
