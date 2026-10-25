# Platform documentation

## Where things are, and what binds

| Location | Content | Binding |
|---|---|---|
| [requirements/](requirements/SRD.md) | What the system must do | yes (draft until IDs are assigned) |
| [architecture/](architecture/system_architecture.md) | [System architecture](architecture/system_architecture.md), [repository model](architecture/repository_model.md) | yes |
| [adr/](adr/README.md) | Consequential decisions | yes, when Accepted |
| [decisions.md](decisions.md) | Log of small decisions ([archive](decisions/2026.md)) | yes |
| [workflow/](workflow/DEVELOPER_GUIDE.md) | How to work: [developer guide](workflow/DEVELOPER_GUIDE.md), [release guide](workflow/RELEASE_GUIDE.md) | procedures |
| [legacy_inventory.md](legacy_inventory.md) | Legacy and archive trees and what they inform | reference |
| [design/](#design-notes) | Proposals, discussions, research and option studies | no |

Official documents (requirements, architecture, ADRs) are short and declarative: they state what
holds, not how it was reached. Explanation, alternatives and detail belong in design notes. A design
note never overrides an official document; when two official documents disagree, fix one and flag
the conflict instead of choosing silently. Design content becomes official through skill
`muon-promote`.

Component specifications live in their repositories (e.g. [core](../../core/SPEC.md)); work
discovery is in [`work/`](../work/README.md).

## Design notes

Each note states its status: `proposed` (input for a future decision) or `reference` (background).

| Note | Status | Topic |
|---|---|---|
| [product_landscape.md](design/product_landscape.md) | reference | Product vision, use cases, deployment modes |
| [instrument_architecture.md](design/instrument_architecture.md) | proposed | Instrument coordination, operating states, interlocks |
| [service_api_shape.md](design/service_api_shape.md) | proposed | External operator/web API |
| [cli_command_model.md](design/cli_command_model.md) | proposed | `muonctl` operator CLI (not the workspace `muon` tool) |
| [instrument_management_bus.md](design/instrument_management_bus.md) | proposed | Future custom slow-control protocol |
| [recon_draft.md](design/recon_draft.md) | proposed | Internal layout of the recon module |
| [deployment_update_report.md](design/deployment_update_report.md) | reference | Option study behind ADR-004 |
| [hardware_abstraction_report.md](design/hardware_abstraction_report.md) | reference | Option study behind ADR-005 |
| [digital_twin_report.md](design/digital_twin_report.md) | reference | Option study behind ADR-007 |
| [simulation_replay_report.md](design/simulation_replay_report.md) | reference | Option study behind ADR-008 |
| [agent_coordination_options.md](design/agent_coordination_options.md) | reference | Agent-coordination tools (2026-10-24) |
