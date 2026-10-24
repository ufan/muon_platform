# Architecture documentation

Start with product context and requirements, then choose the architecture view needed for the task.
Architecture documents describe the current design; component specs define implementation acceptance,
and linked ADRs explain decisions. An architectural target is not evidence of implementation.

| Document | Owns |
|---|---|
| [Architecture overview](architecture_overview.md) | Coarse technical map, processing boundaries and downstream contract questions; domain iteration step 0. |
| [System architecture](system_architecture.md) | Detailed whole-instrument composition, services, three information planes, scientific processing, conditions/time, replay, digital twin, deployment and unresolved design points. |
| [Repository model](repository_model.md) | Repository responsibilities, dependency directions, contract placement and extraction triggers. |

Other sources have distinct responsibilities:

- [Product landscape](../product_landscape.md): mission, use cases, deployment modes and product evolution.
- [Requirements](../requirements/SRD.md): required behavior and acceptance constraints, with subsystem specifications alongside it.
- [Core specifications](../../../core/SPEC.md): implemented/planned scientific component behavior and acceptance links.
- [ADR index](../adr/README.md): rationale, status and explicit supersession relationships.
- [Developer guide](../workflow/DEVELOPER_GUIDE.md): workspace procedures; [work protocol](../../work/README.md): session scope and assignments.
- [Engineering context](../engineering_context.md): concise cross-cutting agent guidance; it is not another master architecture specification.

## Consolidation and maintenance

The former `platform_architecture.md` duplicated whole-system material and now redirects to the
system architecture. Its useful material was retained or assigned to an existing authoritative home:

| Earlier material | Current home |
|---|---|
| Product vision, applications and evolution | Product landscape; not repeated as another product specification. |
| Hardware, services, reconstruction/EDM, storage, acquisition/replay, simulation, digital twin and deployment | System architecture, with decision references and target/implementation qualifications. |
| Repository sketches | Repository model; obsolete monorepo sketches are not current guidance. |
| AI workflow and agent rules | Developer guide, work protocol and existing agent instructions. |
| Numerical/technology ambiguities | System architecture §10; no silent promotion to requirements. |

Keep these scopes separate. Update the owner document and its links rather than creating another
master specification. Architecture filenames use lowercase. Active work belongs in the work index
and task records, not architecture status tables. Historical ADRs and proposals retain their rationale;
flag contradictions and follow explicit supersession rather than assuming newer prose wins.
