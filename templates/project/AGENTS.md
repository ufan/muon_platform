# Platform context

- This project is the `<name>` west project (maturity `incubating`) in the muon platform workspace. Platform-wide rules: `../platform/AGENTS.md` (also generated at the workspace root). Rules in this file add to them.
- Specification index: [SPEC.md](SPEC.md).
- Cross-project contracts come from the `contracts` project at the pinned revision. Never copy them here.
- Verify with `<verify command>` (plain shell, from the repository root). West is never required inside this repo.
- Legacy references (read-only, locked on disk with commits and pushes disabled; never edit, build in place, or depend on them):
  - `../legacy/<dir>`: <what it is a reference for>.
  - Fetch and lock them with `muon-ws refs sync` (or `west refs sync`). Build legacy code only in `muon-ws refs build-dir <name>`.
- Prototype lane (ADR-010 §8): prototyping inside this repo needs no platform change proposal. A proposal is needed only to change `contracts/`, or to promote prototype behaviour into the spec baseline.
- If `../platform` does not exist, this repository is checked out on its own. Follow this file. Platform docs are at `ufan/muon_platform` on GitHub. Set up with `uv tool install "git+https://github.com/ufan/muon_platform#subdirectory=tools/muon_ws"`, then `muon-ws refs sync` and `muon-ws agents sync`.

# Development workflow

<project-specific rules: languages, test policy, hardware access, ...>
