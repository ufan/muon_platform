# ADR-004 Deployment, updates and versions

Status: Accepted (re-baselined 2026-10-25; confirmed by owner 2026-10-26). Option study: [deployment and update report](../design/deployment_update_report.md).

## Decision

- Target: Linux ARM64 edge appliance (and Linux desktops); development on x86_64.
- systemd manages service lifecycle. Software ships as Debian packages first.
- Atomic OTA (RAUC, Mender or SWUpdate) is reserved for production scale.
- Configuration, calibration and geometry are versioned data, never compiled into software.
- An instrument release identifies hardware, firmware, software, algorithm, calibration and
  configuration versions together.

## Why

Instruments live 5–10 years in the field, need offline and remote maintenance, and must reproduce
any past state.

## Consequences

- The instrument release manifest (bill of materials) starts with the first instrument release
  ([ADR-012 §6](ADR-012_repository_baseline_and_workflow.md#6-staged-rigor)).
