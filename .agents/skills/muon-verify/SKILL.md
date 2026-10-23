---
name: muon-verify
description: Use before claiming any task in the muon workspace is done. Runs muon verify for the affected repositories and checks the definition of done.
---

# Verify

1. Run `muon verify <repo…>` for every repository you changed and read the full output. In a plain clone
   without the tool, run the `verify` command from the repository's `.muon/repo.yml`.
2. If a repository has no `verify` command, say so. Do not claim it was verified.
3. Check the definition of done:
   - tests that cover the change name the requirement IDs (CTest labels, test names);
   - `SPEC.md` or the docs describe the behaviour;
   - contract changes are in `core/contracts/` (or `contracts/` after extraction), not copied;
   - `muon agents sync --check` passes if rules, skills or repos files changed;
   - `muon legacy status` shows every legacy reference as LOCKED;
   - `muon status` shows no unexpected dirty repository or branch.
4. Report faithfully: what passed, what was skipped, and which hardware validation was not performed.
