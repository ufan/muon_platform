# ADR-005 Domain controllers

Status: Accepted (re-baselined 2026-10-25). Option study: [hardware abstraction report](../design/hardware_abstraction_report.md).

## Decision

- Each hardware domain has a domain controller that owns its deterministic control, safety and
  interlocks. Central software orchestrates, fuses data, reconstructs and communicates externally.
- A domain controller may be firmware on its own board or a software adapter on the host
  ([ADR-014](ADR-014_slow_control_domains_and_transports.md)); either way it sits behind the
  domain's service interface ([ADR-003](ADR-003_hardware_domain_services.md)).
- DAQ uses a dedicated high-rate link (USB today, possibly Ethernet), separate from slow control.
- Firmware for custom controllers uses Zephyr.

## Why

Local control keeps safety and timing independent of the host and its software; stable interfaces
let controllers change without touching central software.

## Consequences

- Each domain specification states which protection runs in the device and which in its controller.
