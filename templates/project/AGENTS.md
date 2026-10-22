# Platform context

- This project is the `<name>` west project (maturity `incubating`) in the muon platform workspace. Platform-wide rules: `../platform/AGENTS.md` (also generated at the workspace root). Rules in this file add to them.
- Specification index: [SPEC.md](SPEC.md).
- Cross-project contracts come from the `contracts` project at the pinned revision. Never copy them here.
- Verify with `<verify command>` (plain shell, from the repository root). West is never required inside this repo.
- Legacy references (read-only, locked on disk with commits and pushes disabled; never edit, build in place, or depend on them):
  - `../legacy/<dir>`: <what it is a reference for>.
  - Fetch and lock them with `west refs sync`. Build legacy code only in `west refs build-dir <name>`.
- Test data: reference datasets as `<id>@<version>` from the `testdata` project; pin them in `tests/golden.yml`; label golden tests `golden` and skip when data is missing. Never write into the data root.
- Prototype lane (ADR-010 §8): prototyping inside this repo needs no platform change proposal. A proposal is needed only to change `contracts/`, or to promote prototype behaviour into the spec baseline.
- Workspace features (legacy references, agent files, skills, test data) come from a west workspace: the platform one, or a repo-rooted one with `west init -m git@github.com:ufan/muon_<name>.git ws && cd ws && west update && west refs sync && west agents-sync`. A plain clone of this repo is enough to build and test (`<verify command>`).

# Development workflow

<project-specific rules: languages, test policy, hardware access, ...>
