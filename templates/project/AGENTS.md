# <name>: agent rules

<one sentence: what this repository is (domain / instrument / support), maturity `incubating`>.
Platform rules: `../platform/AGENTS.md` (also generated at the workspace root).

## Read first (every AI tool)

In a muon workspace, start by reading `../platform/AGENTS.md`. It holds the workspace rules, which some
tools do not load automatically from outside this repository. Then follow the session protocol:
- follow the `muon-session` skill and `../platform/work/README.md`: explicit assignments first;
  otherwise use `../platform/work/index.yml` for orientation, without automatically taking work;
- verify and commit scoped changes; update only the relevant assigned handoff. Discussion alone
  requires no repository edits. Parallel workers report results to their integrator.

- Spec index: [SPEC.md](SPEC.md). Detailed working guidance (if any): `doc/guides/`.
- Dependencies (platform ADR-012 §4): system contracts only. Never depend on core or on other domains.
- Legacy references (read-only, never a dependency): `../legacy/<dir>` (<what it informs>).
- Test data: `<id>@<version>` pinned in `tests/golden.yml`. Missing data is an explicit skip.
- Verify: `<verify command>` (plain shell, from this directory; `muon verify <name>` in a workspace).

<project-specific hard rules: languages, test policy, hardware access, ...>
