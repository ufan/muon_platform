# Platform documentation

Read in this order. The documents are revised often; when they disagree, the more specific ADR
or architecture document wins and the conflict is flagged (see `../AGENTS.md`).

| # | Section | What it answers |
|---|---|---|
| 1 | [product_landscape.md](product_landscape.md) | What the instrument is for: mission, application domains, deployment modes, system composition |
| 2 | [requirements/](requirements/) | What the system must do (SRD, subsystem requirements) |
| 3 | [Architecture index](architecture/readme.md) | Overview for the coarse map, system architecture for detailed design, repository model for boundaries and dependencies |
| 4 | [ADR topic and status index](adr/README.md) | Decisions that constrain implementation, numbered `ADR-NNN` |
| 5 | [workflow/](workflow/) | How to work in the workspace: [DEVELOPER_GUIDE.md](workflow/DEVELOPER_GUIDE.md); releasing tools: [RELEASE_GUIDE.md](workflow/RELEASE_GUIDE.md) |
| 6 | [guide/](guide/) | Design notes that are not (yet) decisions |
| — | [Work discovery and session scope](../work/README.md) | Active iteration index, explicit assignments, human and batch sessions |
| — | [decisions.md](decisions.md) | Dated log of small decisions (shared memory for every session and tool) |
| — | [engineering_context.md](engineering_context.md) | Product, architecture and engineering rules for agents (moved out of `AGENTS.md`) |
| — | [legacy_inventory.md](legacy_inventory.md) | Managed legacy projects (`legacy/`) and host-local archive trees (`archive/`), and what each one informs |

Outside `docs/`, the platform repository holds the workspace machinery: `repos/` (the repositories, in vcs2l
format), `tools/muon/` (the `muon` CLI), `AGENTS.md` (rules for all AI tools), `changes/` (change
records), `templates/` (new-repository skeleton) and `.agents/skills/` (playbook skills). See ADR-012.
