# Online Data Pipeline

Status: historical. The content of this design note was migrated on 2026-10-24; the former text is in
git history. Live/replay ingress is specified in core under `daq/doc/specs/` (the DAQ module owns the
replay read interface); decode and event building belong to the future `preprocess` and `recon` modules.

| Former section | Current home |
|---|---|
| Purpose, scope, shared architecture, design rule summary | [System architecture §7](../architecture/system_architecture.md#7-offline-data-replay-and-digital-twin); [acquisition sources](../../../core/daq/doc/specs/acquisition-sources.md) |
| Operating modes; what must be identical / may differ; pacing, clock, backpressure, sink policies | [Acquisition sources](../../../core/daq/doc/specs/acquisition-sources.md#identical-in-every-mode), [mode-specific policies](../../../core/daq/doc/specs/acquisition-sources.md#mode-specific-policies) |
| Domain ownership, repository layout impact | [Repository model](../architecture/repository_model.md) and [system architecture §5](../architecture/system_architecture.md#5-scientific-data-path) |
| Canonical contracts (raw stream input, `decoded_board_frame`, `event_frame`) | [Pipeline record contracts](../../../core/contracts/science/pipeline/README.md) (proposed) |
| Observability outputs, stage-local subscription points | [Observation points](../../../core/daq/doc/specs/acquisition-sources.md#observation-points); [event-builder observability](../../../core/daq/doc/specs/event-builder.md#observability) |
| Source adapter contract | [Source adapter](../../../core/daq/doc/specs/acquisition-sources.md#source-adapter) |
| Publisher contract | [Event-builder publication](../../../core/daq/doc/specs/event-builder.md#publication) |
| Failure handling | [Reproducing failures](../../../core/daq/doc/specs/acquisition-sources.md#reproducing-failures); [failure surfacing](../../../core/daq/doc/specs/event-builder.md#failure-surfacing) |
| Minimal deployment shape | [Reference design (non-normative)](../../../core/daq/doc/specs/acquisition-sources.md#reference-design-non-normative) |
