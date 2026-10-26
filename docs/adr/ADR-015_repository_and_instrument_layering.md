# ADR-015 Repository and instrument layering

Status: Accepted (2026-10-23 as part of the former ADR-012; restated 2026-10-26 when the workflow
ADRs were retired)
Related: [repository model](../architecture/repository_model.md) (repositories, dependencies, contract ownership)

## Decision

- Every technical domain has its own repository. `muon_core` is the scientific domain (DAQ,
  preprocess, reconstruction, scientific contracts) and is one domain among several.
- An **instrument** layer above the domains coordinates them: operating modes, sequencing,
  interlock policy, aggregation and operator access. It commands every domain, core included.
- Dependencies point one way. Domains depend only on system contracts, never on each other or on
  core. Core consumes other domains' data only as telemetry/conditions, and never commands them.
- Split a repository only when toolchain, lifecycle or audience/ownership differs. A different
  deployment target is a packaging concern; successive processing stages are not a reason to split.

## Why

The hardware domains (HV, gas, LV, pose, environment) have lifecycles separate from the detector
and are integrated by a central controller. The detector domain produces what customers want and
consumes other domains' data without coordinating them; making it the hub would couple everything
to it. Supervisory systems separate coordination the same way (spacecraft bus and payload,
observatory control systems, ISA-88).

## Alternatives

- **Core as the hub** that coordinates the hardware domains: rejected, it couples every domain to
  the scientific code and its release cycle.
- **One repository per processing stage** (DAQ, preprocess, recon): rejected; online and offline
  share library targets, and co-evolving stages stay together until a split-test difference appears.

## Consequences

- Shared system contracts are staged in `core/contracts/system/` and extracted to `muon_contracts`
  when a second domain or the first instrument starts ([engineering process](../workflow/engineering_process.md#5-staged-rigor)).
- The instrument's release manifest is the product bill of materials.
