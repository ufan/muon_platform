# ADR-003 Instrument services

Status: Accepted (re-baselined 2026-10-25)

## Decision

- Each hardware domain (DAQ, HV, gas, LV, pose, environment) is exposed through a domain service.
- Services expose capabilities, never registers. Applications and orchestration never access
  hardware directly.
- Service interfaces use protobuf/gRPC; other messaging (e.g. Zenoh) only for a demonstrated need.
- Every service has lifecycle, status, health, alarms and capabilities, and a simulator or fake
  backend.

## Why

Domains have separate hardware and lifecycles; stable service contracts let them evolve, be
simulated and be tested independently.

## Consequences

- The instrument coordinates domains through these APIs ([ADR-012](ADR-012_repository_baseline_and_workflow.md)).
- Scientific algorithms are not services ([ADR-001](ADR-001_reconstruction_runtime.md)).
