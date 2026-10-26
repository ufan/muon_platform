---
name: muon-new-project
description: Use when adding a repository (domain, instrument, support or legacy) to the muon workspace. Applies the ADR-015 split test and uses platform/templates/project/.
---

# New repository

## Domain, instrument or support repository

1. Split test (ADR-015). Is there a different toolchain, lifecycle or audience/ownership? If not,
   add a directory to an existing repository and stop. A different deployment target alone is not a reason.
2. Ask the user to create `ufan/muon_<name>` on GitHub, or get approval for `gh repo create`.
3. Copy `platform/templates/project/` and fill in the placeholders. Write `.muon/repo.yml` with `maturity`
   (normally `incubating`), `role`, `spec` and `verify`. The verify command is a plain shell command run
   from the repo root, with no workspace tool. Internal tooling (west, Conan, pixi, …) is the repository's own choice.
4. Respect the dependency rules (ADR-015, repository model): domains depend only on system contracts, and never on core
   or on each other.
5. Add an entry to `platform/repos/workspace.repos`, then run `muon ws sync`, `muon verify <name>` and
   `muon agents sync`.
6. Commit in `platform` with the reason. Add a line to `governance/decisions.md` only if the rationale is not
   recorded elsewhere (its log test). Do not push without confirmation.

## Legacy reference

1. Add an entry to `platform/repos/legacy.repos`: path `legacy/<dir>`, the original remote, a fixed
   version (preferably the tag `legacy-final`), and `muon: {maturity: legacy, informs: [...], role: ...}`.
2. A tree with no remote cannot be reproduced. Propose pushing it to `ufan/muon_legacy_<dir>`, or put it in
   `archive/<dir>` (host-local, not managed).
3. Run `muon ws sync --legacy`, then `muon legacy status` (it must show LOCKED), then `muon agents sync`.
4. Add a row to `platform/docs/legacy_inventory.md`.
