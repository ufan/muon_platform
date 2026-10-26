# ADR-004 Deployment and updates

Status: Accepted (re-baselined 2026-10-25; confirmed by owner 2026-10-26)

## Decision

- Target: Linux ARM64 edge appliance (and Linux desktops); development on x86_64.
- systemd manages service lifecycle. Software ships as Debian packages first.
- Atomic OTA (RAUC, Mender or SWUpdate) is reserved for production scale.
- Configuration, calibration and geometry are versioned data, never compiled into software.

## Why

Instruments live 5–10 years in the field, need offline and remote maintenance, and must reproduce
any past state.

## Alternatives

- Containers: extra runtime and awkward hardware access; possible later for server or cloud
  parts, not for hardware services.
- AppImage or custom bundles: rejected, weak dependency management for a long-lived product.
- OTA tool (RAUC, Mender, SWUpdate): choice deferred to production scale.

## Consequences

- The instrument release manifest (bill of materials) starts with the first instrument release
  ([ADR-012 §6](ADR-012_repository_baseline_and_workflow.md#6-staged-rigor)).

## Open

- Release and version model: not decided. Rough idea: layered tiers (hardware and firmware;
  software; algorithms; data, i.e. calibration and configuration).
