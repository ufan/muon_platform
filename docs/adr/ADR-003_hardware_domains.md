# ADR-003 Hardware domains: services and controllers

Status: Accepted (re-baselined 2026-10-25; confirmed by owner 2026-10-26; former ADR-005 merged in 2026-10-26)
Related: [ADR-014](ADR-014_slow_control_transports.md) (transports and stages)

## Decision

Software reaches hardware through three layers: domain service → domain controller → transport.

- **Domain service.** Each hardware domain (DAQ, HV, gas, LV, pose, environment) is exposed
  through a domain service. Services expose capabilities, never registers; applications and
  orchestration never access hardware directly.
- Every service has lifecycle, status, health, alarms and capabilities, and a simulator or fake
  backend.
- Service interfaces use protobuf/gRPC; other messaging (e.g. Zenoh) only for a demonstrated need.
- **Domain controller.** Each domain has a controller that owns its deterministic control, safety
  and interlocks. It may be firmware on its own board or a software adapter on the host; either way
  it sits behind the domain service. Central software orchestrates, fuses data, reconstructs and
  communicates externally.
- **Transport** is configuration, chosen per device ([ADR-014](ADR-014_slow_control_transports.md)).
- DAQ uses a dedicated high-rate link (USB today, possibly Ethernet), separate from slow control.

## Why

Domains have separate hardware and lifecycles. Stable service contracts let them evolve, be
simulated and be tested independently; local control keeps safety and timing independent of the
host's other software, and lets controllers change without touching central software.

## Alternatives

- Orchestration or application code driving devices directly, with no domain controller:
  rejected, safety and timing logic would spread across unrelated software.
- One universal instrument bus: rejected. Modbus RTU lacks bandwidth and typing, CAN-FD payloads
  are small, and neither carries DAQ streams.

## Consequences

- The instrument coordinates domains through these APIs ([ADR-012](ADR-012_repository_baseline_and_workflow.md)).
- Scientific algorithms are not services ([ADR-001](ADR-001_reconstruction_runtime.md)).
- Each domain specification states which protection runs in the device and which in its controller.
