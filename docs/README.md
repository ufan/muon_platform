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

Note content becomes baseline through skill `muon-promote` (see the [developer guide](../governance/developer_guide.md#5-exploration--baseline--controlled)).

ADRs carry their own status (proposed, accepted, partly superseded); see the [ADR index](adr/README.md).
Only `current` documents, accepted ADRs and component specifications bind implementation.
Product ADRs were re-baselined on 2026-10-25 into short decisions; the workflow ADRs were retired
on 2026-10-26 into the [engineering process](../governance/engineering_process.md).

| # | Section | What it answers |
|---|---|---|
| 1 | [requirements/](requirements/system_requirements.md) | What the instrument is for (product, applications, deployment modes) and what it must do |
| 2 | [architecture/](architecture/system_architecture.md) | [System architecture](architecture/system_architecture.md): principles, composition, services, planes, the scientific data path (§5), conditions, deployment; [repository model](architecture/repository_model.md): boundaries and dependencies |
| 3 | [ADR topic and status index](adr/README.md) | Decisions that constrain implementation, numbered `ADR-NNN` |
| 4 | [Notes](#notes) | Proposals, research and historical records; not decisions |
| — | [Work discovery and session scope](../work/README.md) | Active iteration index, explicit assignments, human and batch sessions |
| — | [governance/](../governance/README.md) | How the project is developed and managed: engineering process, guides, decision log (outside `docs/`) |
| — | [context.md](context.md) | Short agent primer: product, where to look, invariants |
| — | [legacy_inventory.md](legacy_inventory.md) | Managed legacy projects (`legacy/`) and host-local archive trees (`archive/`), and what each one informs |

## Notes

`notes/` holds proposals, research and the records left after promotion; none of it is normative. Process documents and how-to
guides live in [`governance/`](../governance/README.md).

| Note | Status | Scope / current home |
|---|---|---|
| [event_builder.md](notes/event_builder.md) | historical | Migrated to `core/daq/doc/specs/event-builder*.md` and `core/contracts/science/pipeline/`; the file maps each former section. |
| [online_pipeline.md](notes/online_pipeline.md) | historical | Migrated to `core/daq/doc/specs/acquisition-sources.md`, the pipeline record contracts and system architecture §7; the file maps each former section. |
| [recon_draft.md](notes/recon_draft.md) | proposed | Internal layout of the future recon module. |
| [instrument.md](notes/instrument.md) | proposed | Instrument layer: orchestration, operating states and policies, operator CLI, external API. |
| [instrument_management_bus.md](notes/instrument_management_bus.md) | proposed | Future custom slow-control protocol (COBS/protobuf RPC); not decided, see ADR-014. |
| [agent_coordination_options.md](notes/agent_coordination_options.md) | reference | Agent-coordination tool research (2026-10-24). |

Outside `docs/`, the platform repository holds the workspace machinery: `repos/` (the repositories, in vcs2l
format), `tools/muon/` (the `muon` CLI), `AGENTS.md` (rules for all AI tools), `iterations/` (system-level
plans), `templates/` (new-repository skeleton) and `.agents/skills/` (playbook skills). See the [engineering process](../governance/engineering_process.md).
