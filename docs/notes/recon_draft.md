# Recon module draft

Status: proposed. Input for the recon iteration; not a decision. Event-builder behaviour and record
fields are already specified in core ([event builder](../../../core/daq/doc/specs/event-builder.md),
[pipeline records](../../../core/contracts/science/pipeline/README.md)); this note covers only the
module layout around them. Trimmed 2026-10-25 (full text in git).

## Scope

`recon` is a module of `core`. It owns the event-domain pipeline after transport decode: event
building, event-frame publication, hit building, tracking and reconstruction diagnostics. Event
building stays inside recon: it works on decoded detector contributions and produces logical
events, so it belongs neither in preprocess nor in a repository of its own.

## Proposed layout

```text
recon/
  event_builder/   assembly of logical events: event table, merge, completion policy, publisher
  hit_builder/     consumes finalized event frames
  tracking/        consumes hit collections
  apps/            online runtime wiring (online_recon_main)
  fixtures/        decoded fragments and events
```

Names may change; the ownership split should not.

## Event-builder seams

```text
push(decoded_board_frame)
poll_expired(now)
flush(run_id)
subscribe(publisher)            publish(event_frame) -> publish_result
```

Keep merge logic pure (first fragment, duplicate, accepted or rejected replacement, coverage
update, warning propagation) so it can be tested without the runtime. A publisher router fans one
event frame out to several sinks and accounts per-sink results.

## Runtime flow

```text
DAQ -> preprocess decode -> decoded_board_frame -> recon::event_builder -> event_frame
    -> publishers -> hit_builder -> tracking
```

Observers may attach to decoded frames, builder metrics, lifecycle notifications and finished
event frames. Preprocess never publishes event frames; the event builder never parses raw bytes.

## Order of work

1. `decoded_board_frame` and `event_frame` contracts in `core/contracts/science/`;
2. `event_builder`, `completion_policy` and `publisher` interfaces;
3. single-process, in-memory first version with coverage and timeout completion, one in-process
   publisher and fixtures for complete, partial, duplicate and corrupt cases; no database, UI,
   imaging or tracking coupling.

Migration from legacy: raw decode stays in preprocess; hit-position logic moves to `hit_builder`,
track search to `tracking`.
