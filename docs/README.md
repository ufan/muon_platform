# Platform documentation

Read in this order. The documents are revised often; when they disagree, the more specific ADR
or architecture document wins and the conflict is flagged (see `../AGENTS.md`).

| # | Section | What it answers |
|---|---|---|
| 1 | [product_landscape.md](product_landscape.md) | What the instrument is for: mission, application domains, deployment modes, system composition |
| 2 | [requirements/](requirements/) | What the system must do (SRD, subsystem requirements) |
| 3 | [architecture/](architecture/) | How the platform is structured; [LANDSCAPE.md](architecture/LANDSCAPE.md) is the coarse map used by every domain iteration |
| 4 | [adr/](adr/) | Decisions that constrain implementation, numbered `ADR-NNN` |
| 5 | [workflow/](workflow/) | How to work in the workspace: [WORKSPACE_GUIDE.md](workflow/WORKSPACE_GUIDE.md) |
| 6 | [guide/](guide/) | Design notes that are not (yet) decisions |
| — | [legacy_inventory.md](legacy_inventory.md) | Legacy code and host-local references, and what each one informs |

Outside `docs/`, the hub root holds workspace machinery: `west.yml` (projects), `AGENTS.md`
(rules for all AI tools), `changes/` (change proposals), `templates/` (new-project skeleton),
`scripts/` (west extensions) and `.agents/skills/` (playbook skills).
