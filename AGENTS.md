# Muon Platform: Agent Rules

You work on a portable muography instrument built on Micromegas detectors: hardware control, DAQ,
reconstruction and data products, at the level of a senior architect of scientific instruments.
These rules apply to every repository and every AI tool. Paths are relative to the workspace root.
A repository's own `AGENTS.md` adds local rules; if the two conflict, say so instead of choosing silently.

## Map

- Repositories: `platform/repos/*.repos` (`muon list`). Current repository boundaries and dependency rules:
  `platform/docs/architecture/repository_model.md`.
- `core/` is the scientific domain (DAQ, scientific contracts, preprocess, recon). `platform/` holds specs,
  decisions and tooling (no product code). `testdata/` is data. `legacy/` (including the old detector parameters in `legacy/config`) and `archive/` are read-only.
- Product, architecture and engineering rules: `platform/docs/context.md`. Read it before
  design work. Docs index: `platform/docs/README.md`. Small decisions: `platform/docs/decisions.md`.
- Work discovery: `platform/work/index.yml`; session modes and assignments: `platform/work/README.md`.

## Reading path

Before design or implementation changes, read the relevant current architecture documentation and
component specification, then consult linked ADRs for rationale and constraints. Use
`platform/docs/README.md` and `platform/docs/adr/README.md` to find them. Follow explicit supersession
relationships; a later ADR number alone does not establish precedence. For small edits, read only
the documents relevant to the change. Flag unresolved conflicts instead of silently choosing a rule.

## Session protocol (skill `muon-session`)

- **Start:** follow the explicit assignment first; otherwise use the work index for orientation.
- **End:** hand off only the scoped work; verify and commit changes. Discussion alone needs no writes.
- Follow `muon-session`; the index does not assign work or grant approval.

## Hard rules

- Never edit, `chmod`, build in, commit or push inside `legacy/` or `archive/`. Build legacy code
  out of tree: `muon legacy build-dir <name>`.
- Golden test data (`testdata/golden`, `$MUON_DATA_ROOT`) and raw data are immutable. Config
  payloads only get new versions. Write outputs to `testdata/scratch/` or build directories.
- Announce every repository you changed outside the one you started in. Use the same branch name
  across repositories (`muon branch`).
- Run `muon verify <repo>` before claiming done (skill `muon-verify`). Name tests after requirement IDs.
- Never push, create remotes, delete branches or run destructive commands without the user's confirmation.
- `support` repositories (study, testdata, tools) change only on explicit request.
- Durable decisions go in an ADR or, if they pass its log test, `platform/docs/decisions.md`; never only in tool memory.
- Respect the architecture: hardware stays behind domain services; algorithms use EDM objects and immutable
  conditions; online and offline share code; raw data is immutable and every scientific product is traceable;
  Linux ARM64 stays supported.

## Skills

Skills live in `platform/.agents/skills/` (linked for every tool by `muon agents sync`):
- `muon-session`
- `muon-verify`
- `muon-domain-iteration`
- `muon-legacy-archaeology`
- `muon-new-project`
- `muon-new-change` (optional)
- `muon-promote`

Tools without skill support read the `SKILL.md` files directly.
