# ADR-001 Reconstruction runtime

Status: Accepted (re-baselined 2026-10-25; confirmed by owner 2026-10-26)

## Decision

- Reconstruction is an internal, configurable DAG of algorithms in one process, not a set of services.
- The first runtime is Taskflow.
- Algorithms exchange only Muon EDM objects ([ADR-002](ADR-002_muon_edm_serialization.md)) and run
  unchanged on live, replayed and simulated data.

## Why

Reconstruction needs low latency, shared memory, deterministic execution and fast algorithm
iteration; service boundaries would add cost without benefit.

## Consequences

- Algorithms can be replaced or reordered by configuration.
- Taskflow stays behind the pipeline interface, so the runtime can change later.
