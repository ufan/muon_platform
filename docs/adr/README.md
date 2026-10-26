# Architecture decision index

## Product and system

Re-baselined on 2026-10-25: each ADR below states the decision in force in short form; the long
option studies behind 004, 005, 007 and 008 are reference [design notes](../README.md#design-notes),
and the earlier text is in git (tag `docs-pre-cleanup`). Owner confirmation of the re-baselined text is noted in each ADR's status line (confirmed so far: 001, 002, 003).

| ADR | Decision | Status |
|---|---|---|
| [001](ADR-001_reconstruction_runtime.md) | Reconstruction is an in-process DAG (Taskflow), not services | Accepted |
| [002](ADR-002_muon_edm_serialization.md) | Muon EDM is the scientific contract; serialization outside algorithms | Accepted |
| [003](ADR-003_hardware_domain_services.md) | Hardware domains behind protobuf/gRPC domain services | Accepted |
| [004](ADR-004_deployment_update_strategy.md) | ARM64 edge, systemd, Debian packages; versioned config; release identity | Accepted |
| [005](ADR-005_hardware_abstraction.md) | Domain controllers own control and safety; DAQ on a dedicated link | Accepted |
| [007](ADR-007_digital_twin_strategy.md) | Layered product architecture with a digital twin | Accepted |
| [008](ADR-008_simulation_verification_replay.md) | Live, replay and simulation are equivalent sources | Accepted |
| [014](ADR-014_slow_control_domains_and_transports.md) | Slow control: stable services, configurable transports, Modbus now | Accepted |

## Development and repositories

| Decision | Recorded status / later changes | Scope and relationships |
|---|---|---|
| [006 — AI-assisted engineering](ADR-006_ai_assisted_engineering_workflow.md) | Not recorded; §2 partly superseded | Repository organization replaced by ADR-009, then ADR-012; spec workflow extended by ADR-010. |
| [009 — Workspace model](ADR-009_workspace_repository_model.md) | Partly superseded | ADR-012 replaces §1–§4, §6–§10, §12–§13; §5, §11, §14–§15 remain with adaptations. |
| [010 — Domain iteration](ADR-010_spec_driven_domain_iteration.md) | Accepted; partly superseded | ADR-012 §3, §5–§6 revise repository/contract placement, tooling and the proposal/prototype rules in §2–§3 and §8; the iteration playbook remains. |
| [012 — Repository baseline and workflow](ADR-012_repository_baseline_and_workflow.md) | Accepted; §8 partly superseded | Repository baseline; replaces parts of ADR-009, revises ADR-010 and amends ADR-011. ADR-013 replaces global iteration discovery and universal iteration handoff. |
| [013 — Work discovery and session scope](ADR-013_work_discovery_and_session_scope.md) | Accepted | Stable instructions, multiple active plans, explicit assignments and scoped human/batch handoffs; replaces those rules in ADR-012 §8. |
| [011 — Test data](ADR-011_test_data.md) | Accepted; amended | 2026-10-23 amendment follows ADR-012 §6 and §8 for multiple hosts. |

## Maintaining the record

- Use ADRs for consequential choices with alternatives and lasting implications. Keep small
  decisions in [decisions.md](../decisions.md) and implementation details in component docs.
- Edit proposed ADRs during review. Correct wording, links and factual errors in place; record
  meaningful clarifications in a revision note.
- For a material change to an accepted decision, add a new ADR. Identify the exact decisions or
  sections it supersedes, and add reciprocal links to the affected ADRs. Preserve their rationale.
- Platform ADR numbers are unqualified (`ADR-006`). A repository's own decision records keep their
  numbering and are qualified outside that repository, like requirement IDs (ADR-010 §7):
  `daq:ADR-006` is the DAQ decision on online event building, not platform ADR-006.
- Distinguish related or extending decisions from replacement. For partial supersession, state
  what remains in force; a later number alone does not override earlier text.
- Update this index and the relevant current architecture or workflow guidance in the same change.
  Keep the flat folder as it grows; expand the topic index rather than renumbering or moving history.
