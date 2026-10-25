# Architecture decision index

Status: current (ADR index).

ADR numbers follow decision-record order and remain stable. They are identifiers, not topic
categories or precedence rules. Keep existing IDs and paths when decisions evolve.

Start with the [architecture](../architecture/architecture_overview.md) and
[developer guide](../workflow/DEVELOPER_GUIDE.md) for current guidance; use ADRs for rationale,
alternatives and history. Explicit replacement relationships determine which decision applies
within their stated scope. Flag contradictions that are not explicitly resolved.

## Decisions by topic

“Not recorded” means the ADR has no formal status field; this index does not infer acceptance.
Topic groups are navigation aids, and a decision may concern several topics.

### Scientific software and data

| Decision | Recorded status / later changes | Scope and relationships |
|---|---|---|
| [001 — Reconstruction runtime](ADR-001_reconstruction_runtime.md) | Not recorded | Internal DAG runtime. |
| [002 — Muon EDM and serialization](ADR-002_muon_edm_serialization.md) | Not recorded | Scientific objects and persistence boundaries. |

### Instrument and deployment

| Decision | Recorded status / later changes | Scope and relationships |
|---|---|---|
| [003 — Instrument services](ADR-003_instrument_service_architecture.md) | Not recorded | Hardware domain service boundaries. |
| [004 — Deployment and updates](ADR-004_deployment_update_strategy.md) | Not recorded | Deployment, lifecycle and versioning. |
| [005 — Hardware abstraction](ADR-005_hardware_abstraction.md) | Not recorded; §1, §5–§6 partly superseded | Domain controllers and interfaces; ADR-014 revises host-side controllers and the bus recommendations. |
| [014 — Slow-control domains and transports](ADR-014_slow_control_domains_and_transports.md) | Accepted | Stable domain service interfaces; host-adapter or on-board domain controllers; transports and ports as configuration; Modbus RTU now, custom protocol and CAN-FD as aspirations; DAQ off the slow-control bus. |

### Development and repositories

| Decision | Recorded status / later changes | Scope and relationships |
|---|---|---|
| [006 — AI-assisted engineering](ADR-006_ai_assisted_engineering_workflow.md) | Not recorded; §2 partly superseded | Repository organization replaced by ADR-009, then ADR-012; spec workflow extended by ADR-010. |
| [009 — Workspace model](ADR-009_workspace_repository_model.md) | Partly superseded | ADR-012 replaces §1–§4, §6–§10, §12–§13; §5, §11, §14–§15 remain with adaptations. |
| [010 — Domain iteration](ADR-010_spec_driven_domain_iteration.md) | Accepted; partly superseded | ADR-012 §3, §5–§6 revise repository/contract placement, tooling and the proposal/prototype rules in §2–§3 and §8; the iteration playbook remains. |
| [012 — Repository baseline and workflow](ADR-012_repository_baseline_and_workflow.md) | Accepted; §8 partly superseded | Repository baseline; replaces parts of ADR-009, revises ADR-010 and amends ADR-011. ADR-013 replaces global iteration discovery and universal iteration handoff. |
| [013 — Work discovery and session scope](ADR-013_work_discovery_and_session_scope.md) | Accepted | Stable instructions, multiple active plans, explicit assignments and scoped human/batch handoffs; replaces those rules in ADR-012 §8. |

### Simulation and verification

| Decision | Recorded status / later changes | Scope and relationships |
|---|---|---|
| [007 — Digital twin strategy](ADR-007_digital_twin_strategy.md) | Not recorded | Product architecture and digital twin. |
| [008 — Simulation and replay](ADR-008_simulation_verification_replay.md) | Not recorded | Equivalent live, replay and synthetic acquisition sources. |
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
