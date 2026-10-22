---
name: muon-verify
description: Use before claiming any task in the muon workspace is done. Runs west verify for the affected projects and checks the definition of done.
---

# Verify

1. In a west workspace, run `west verify <projects>` (or `-g <group>`). Without a workspace (plain clone), run the project's plain verify command from its `AGENTS.md`. Read the full output.
2. If a project has no `verify` command in `platform/west.yml`, say so explicitly. Do not claim it was verified.
3. Check the definition of done:
   - the tests that cover the change reference spec or requirement IDs;
   - the project `SPEC.md` or docs reflect the behaviour;
   - contract changes are in `contracts/`, not copied into consumers;
   - `west agents-sync --check` passes if rules, skills or a manifest changed;
   - `west legacy status` shows every managed legacy project LOCKED.
4. Report results faithfully, including skipped checks and any hardware validation not performed.
