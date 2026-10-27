# Architecture decision index

Status: current (index).

## Product and system

Re-baselined on 2026-10-25: each ADR below states the decision in force in short form, with its
alternatives where they mattered; the earlier long text and option studies are in git (tag
`docs-pre-cleanup`). All were confirmed by the owner on 2026-10-26 (005 merged into 003). ADR-011 keeps its
original form; ADR-015 restates the repository layering of the retired ADR-012.

Grouped by topic; numbers are permanent identifiers and are never reused or renumbered.

### Scientific processing and data

| ADR | Decision | Status |
|---|---|---|
| [001](ADR-001_reconstruction_runtime.md) | Reconstruction is an in-process DAG (Taskflow), not services | Accepted |
| [002](ADR-002_muon_edm_serialization.md) | Muon EDM is the scientific contract; serialization outside algorithms | Accepted |
| [008](ADR-008_data_sources_and_verification.md) | Offline data for components, live and replay for the online pipeline; no physics simulation | Accepted |
| [011](ADR-011_test_data.md) | Versioned, immutable test datasets; bytes host-local, catalog in git | Accepted; amended 2026-10-23 |

### Hardware domains

| ADR | Decision | Status |
|---|---|---|
| [003](ADR-003_hardware_domains_services_and_controllers.md) | Hardware domains: services and controllers. gRPC domain services over controllers that own control and safety; DAQ on a dedicated link | Accepted |
| [014](ADR-014_hardware_domains_transports.md) | Hardware domains: slow-control transports. Device map, bus owner per port, Modbus RTU now | Accepted |

### Product and deployment

| ADR | Decision | Status |
|---|---|---|
| [007](ADR-007_digital_twin.md) | Layered product architecture with a digital twin | Accepted |
| [004](ADR-004_deployment_and_updates.md) | ARM64 edge, systemd, Debian packages; versioned config; version model open | Accepted |

### Repositories

| ADR | Decision | Status |
|---|---|---|
| [015](ADR-015_repository_and_instrument_layering.md) | One repository per domain; an instrument layer coordinates; dependencies point one way | Accepted |

## Retired

| ADR | Topic | Status |
|---|---|---|
| 005 | Domain controllers | Merged into 003 (2026-10-26) |
| 006 | AI-assisted engineering | Retired 2026-10-26 |
| 009 | Workspace and repository model | Retired 2026-10-26 |
| 010 | Spec-driven domain iteration | Retired 2026-10-26 |
| 012 | Repository baseline and workflow | Retired 2026-10-26; repository layering restated as ADR-015 |
| 013 | Work discovery and session scope | Retired 2026-10-26 |

Project-management rules from 006, 009, 010, 012 and 013 now live in the
[engineering process](../../governance/engineering_process.md); their text is in git. Numbers are not reused.

## Maintaining the record

- Use ADRs for consequential choices with alternatives and lasting implications. Small
  decisions live in the document they change (a [decision log](../../governance/decision_log.md)
  entry may point to it) and implementation details in component docs.
- Edit proposed ADRs during review. Correct wording, links and factual errors in place; record
  meaningful clarifications in a revision note.
- For a material change to an accepted decision, add a new ADR. Identify the exact decisions or
  sections it supersedes, and add reciprocal links to the affected ADRs. Preserve their rationale.
- Platform ADR numbers are unqualified (`ADR-006`). A repository's own decision records keep their
  numbering and are qualified outside that repository, like requirement IDs ([engineering process §3](../../governance/engineering_process.md#3-requirement-ids)):
  `daq:ADR-006` is the DAQ decision on online event building, not platform ADR-006.
- Distinguish related or extending decisions from replacement. For partial supersession, state
  what remains in force; a later number alone does not override earlier text.
- Update this index and the relevant current architecture or workflow guidance in the same change.
  Keep the flat folder as it grows; expand the topic index rather than renumbering or moving history.
