---
name: muon-new-project
description: Use when adding a new repository (component or legacy reference) to the muon platform workspace. Walks the checklists in platform/04_workflow/WORKSPACE_GUIDE.md §4–§5 using platform/templates/project/.
---

# New project

Read `platform/04_workflow/WORKSPACE_GUIDE.md` §4 (new repository) or §5 (legacy repository) first.

## New component repository

1. Check the split rule (ADR-009 §4): is there a different lifecycle, toolchain, deployment target or audience? If not, add a directory to an existing repo instead, and stop.
2. Ask the user to create `ufan/muon_<name>` on GitHub, or get approval to run `gh repo create`.
3. Copy `platform/templates/project/` into the new repo and fill in the placeholders (`<name>`, role, verify command).
4. Make sure the verify command is a plain shell command that runs from the repo root **without west**.
5. Add the project to `platform/west.yml`, or let it carry its own `west.yml` (ADR-009 §13): `name`, `path`, `repo-path`, `revision`, `groups`, and `userdata: {role, maturity: incubating, deploy, spec, verify}`.
6. Run `west catalog -a`, then `west verify <name>`, then `west agents-sync`.
7. Commit the manifest change in `platform` with the reason. Do not push without confirmation.

## Legacy repository

1. Path `legacy/<dir>`, west name `<dir>-legacy` (underscores become dashes), `groups: [legacy]`, `maturity: legacy`, and an explicit `reference_for: [...]`.
2. Keep its original remote and pin a fixed revision (preferably a tag `legacy-final`).
3. Declare it in the one repo that uses it (its `west.yml`). If several repos use it, declare it in `platform/west.yml` (ADR-009 §13).
4. A repo with no remote cannot be reproduced elsewhere. Propose pushing it to `ufan/muon_legacy_<dir>`, or record it as local-only.
5. Run `west refs sync <name>` (clone + lock), then `west refs status`, then `west agents-sync`.
6. Add a row to `platform/legacy_inventory.md`.
