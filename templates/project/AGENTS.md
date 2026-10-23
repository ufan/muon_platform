# <name>: agent rules

<one sentence: what this repository is (domain / instrument / support), maturity `incubating`>.
Platform rules: `../platform/AGENTS.md` (also generated at the workspace root).

- Spec index: [SPEC.md](SPEC.md). Detailed working guidance (if any): `doc/guides/`.
- Dependencies (platform ADR-012 §4): system contracts only. Never depend on core or on other domains.
- Legacy references (read-only, never a dependency): `../legacy/<dir>` (<what it informs>).
- Test data: `<id>@<version>` pinned in `tests/golden.yml`. Missing data is an explicit skip.
- Verify: `<verify command>` (plain shell, from this directory; `muon verify <name>` in a workspace).

<project-specific hard rules: languages, test policy, hardware access, ...>
