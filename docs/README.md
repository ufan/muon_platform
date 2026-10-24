# Platform documentation

Status: current (documentation index).

Read in this order. The documents are revised often. When they disagree, authority comes from each
document's declared scope and status and from explicit supersession, not from specificity, filename
or ADR number; flag conflicts that are not explicitly resolved (see `../AGENTS.md`).

Every document states its status under the title:

| Status | Meaning |
|---|---|
| `current` | Authoritative for its declared scope. |
| `draft` | Requirements baseline under construction; binding only where it says so. |
| `proposed` | Design input, not a decision. Do not implement from it without a decision or component spec. |
| `proposed, partly promoted` | As `proposed`, with a table under the status line mapping the sections already promoted to their current homes. |
| `reference` | Background or dated research. |
| `historical` | Kept for rationale; names its current home. |

Guide content becomes baseline through skill `muon-promote` (see the [developer guide](workflow/DEVELOPER_GUIDE.md#5-prototype--baseline)).

ADRs carry their own status (proposed, accepted, partly superseded); see the [ADR index](adr/README.md).
Only `current` documents, accepted ADRs and component specifications bind implementation.
ADR-001…008 have no recorded status yet: rely on the constraints that current architecture documents
carry forward from them, and flag anything asserted only by one of those ADRs.

| # | Section | What it answers |
|---|---|---|
| 1 | [product_landscape.md](product_landscape.md) | What the instrument is for: mission, application domains, deployment modes, system composition |
| 2 | [requirements/](requirements/) | What the system must do (SRD, subsystem requirements) |
| 3 | [Architecture index](architecture/readme.md) | Overview for the coarse map, system architecture for detailed design, repository model for boundaries and dependencies |
| 4 | [ADR topic and status index](adr/README.md) | Decisions that constrain implementation, numbered `ADR-NNN` |
| 5 | [workflow/](workflow/) | How to work in the workspace: [DEVELOPER_GUIDE.md](workflow/DEVELOPER_GUIDE.md); releasing tools: [RELEASE_GUIDE.md](workflow/RELEASE_GUIDE.md) |
| 6 | [Guides](#guides) | Design notes that are not (yet) decisions |
| — | [Work discovery and session scope](../work/README.md) | Active iteration index, explicit assignments, human and batch sessions |
| — | [decisions.md](decisions.md) | Dated log of small decisions (shared memory for every session and tool) |
| — | [engineering_context.md](engineering_context.md) | Product, architecture and engineering rules for agents (moved out of `AGENTS.md`) |
| — | [legacy_inventory.md](legacy_inventory.md) | Managed legacy projects (`legacy/`) and host-local archive trees (`archive/`), and what each one informs |

## Guides

| Guide | Status | Scope / current home |
|---|---|---|
| [event_builder.md](guide/event_builder.md) | historical | Migrated to `core/daq/doc/specs/event-builder*.md` and `core/contracts/science/pipeline/`; the file maps each former section. |
| [online_pipeline.md](guide/online_pipeline.md) | historical | Migrated to `core/daq/doc/specs/acquisition-sources.md`, the pipeline record contracts and system architecture §7; the file maps each former section. |
| [recon_draft.md](guide/recon_draft.md) | proposed | Internal layout of the future recon module. |
| [instrument_architecture.md](guide/instrument_architecture.md) | proposed | Instrument coordination, operating states and interlocks for the planned `muon_instrument`. |
| [service_api_shape.md](guide/service_api_shape.md) | proposed | External operator/web API shape; internal services stay protobuf/gRPC. |
| [cli_command_model.md](guide/cli_command_model.md) | proposed | `muonctl` operator CLI (not the workspace `muon` tool). |
| [agent-coordination-options.md](guide/agent-coordination-options.md) | reference | Agent-coordination tool research (2026-10-24). |
| [repo_boundaries.md](guide/repo_boundaries.md) | historical | Current home: [repository model](architecture/repository_model.md). |
| [prompt.md](guide/prompt.md) | historical | Original project brief; current home: product landscape and ADR-012. |

Outside `docs/`, the platform repository holds the workspace machinery: `repos/` (the repositories, in vcs2l
format), `tools/muon/` (the `muon` CLI), `AGENTS.md` (rules for all AI tools), `changes/` (change
records), `templates/` (new-repository skeleton) and `.agents/skills/` (playbook skills). See ADR-012.
