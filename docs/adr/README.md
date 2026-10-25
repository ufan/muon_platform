# Architecture decisions

| ADR | Decision | Status |
|---|---|---|
| [001](ADR-001_reconstruction_runtime.md) | Reconstruction is an in-process DAG (Taskflow), not services | Accepted |
| [002](ADR-002_muon_edm_serialization.md) | Muon EDM is the scientific contract; serialization outside algorithms | Accepted |
| [003](ADR-003_instrument_service_architecture.md) | Hardware domains behind protobuf/gRPC domain services | Accepted |
| [004](ADR-004_deployment_update_strategy.md) | ARM64 edge, systemd, Debian packages; versioned config; release identity | Accepted |
| [005](ADR-005_hardware_abstraction.md) | Domain controllers own control and safety; DAQ on a dedicated link | Accepted |
| [006](ADR-006_ai_assisted_engineering_workflow.md) | AI-assisted workflow | Superseded by 010, 012, 013 |
| [007](ADR-007_digital_twin_strategy.md) | Layered product architecture with a digital twin | Accepted |
| [008](ADR-008_simulation_verification_replay.md) | Live, replay and simulation are equivalent sources | Accepted |
| [009](ADR-009_workspace_repository_model.md) | Workspace model (west) | Superseded by 012 |
| [010](ADR-010_spec_driven_domain_iteration.md) | Spec-driven domain iteration playbook, spec layers, requirement IDs | Accepted |
| [011](ADR-011_test_data.md) | Test data in `muon_testdata`, immutable `id@version` | Accepted |
| [012](ADR-012_repository_baseline_and_workflow.md) | Repository baseline, `muon` tooling, staged rigor, legacy guardrails | Accepted |
| [013](ADR-013_work_discovery_and_session_scope.md) | Work index for orientation; explicit assignments decide scope | Accepted |
| [014](ADR-014_slow_control_domains_and_transports.md) | Slow control: stable services, configurable transports, Modbus now | Accepted |

ADRs 001–013 were re-baselined on 2026-10-25: each now states the decision in force, without
section-level supersession notes. The earlier long texts are in git (tag `docs-pre-cleanup`); the
option studies behind 004, 005, 007 and 008 are kept as reference notes in [`design/`](../design/).

## Rules

- An ADR records a consequential choice with alternatives: decision, reasons, consequences, in a
  page or less. Small decisions go in the [decision log](../decisions.md); explanation and option
  studies go in `design/`.
- Accepted ADRs change only by a new ADR that names what it replaces; mark the old one superseded.
- Numbers are stable identifiers. Other repositories' decision records are qualified:
  `daq:ADR-006` is a DAQ decision, not platform ADR-006.
