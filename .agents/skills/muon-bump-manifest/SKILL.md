---
name: muon-bump-manifest
description: Use when a cross-repository change is ready to integrate, or a project changes revision, remote, maturity or groups. Updates platform/west.yml (ADR-009 §8).
---

# Bump manifest

1. Confirm each affected project's change is committed. Use `git -C <path> log -1` to get the commit or tag.
2. In `platform/west.yml`, update `revision:` for each project (prefer tags for releases), or update `remote:`, `groups:` or `userdata.maturity` as needed.
3. Run:
   - `west list` (manifest parses);
   - `west catalog -a`;
   - `west verify` for the affected groups;
   - `west agents-sync`, then commit the regenerated root files if this workspace tracks them.
4. Commit in `platform` with the change proposal slug in the message.
5. For a release snapshot: `west manifest --freeze -o platform/releases/<version>.yml`.
6. Never run `west update` on projects with local work, and never push without the user's confirmation. Legacy projects are updated only with `west refs sync --update <name>`, which keeps them locked.
