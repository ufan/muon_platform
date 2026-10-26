# ADR-011 Test Data Management

Version: 1.0
Status: Accepted (2026-10-22); amended 2026-10-23
Related: [ADR-008](ADR-008_data_sources_and_verification.md) (data sources), [engineering process](../../governance/engineering_process.md) (golden data in domain iterations, hardening triggers)

## Decision

Test datasets (real recorded data used for testing, verification, replay and demos) are
managed by a **dedicated, self-managed repository `muon_testdata`** (workspace path `testdata/`),
not by the platform hub.

- The repository holds only the **catalog and the tool** (`catalog.yml`, `tools/testdata.py`,
  `README.md`). The **bytes stay local** on each host, git-ignored, in a read-only data root
  (default `testdata/golden/`, override `MUON_DATA_ROOT`).
- Datasets are addressed as immutable **`<id>@<version>`**:
  - modifying a dataset creates the next version, hard-linking unchanged files;
  - deleting one marks the version retired;
  - local bytes are removed only by an explicit prune.
- Each change is one reviewed commit in `muon_testdata`. The workspace tracks that repository's
  `main` (`platform/repos/workspace.repos`), so dataset changes never touch the platform history.
  `muon freeze` still records the exact catalog commit.
- Consumers **pin** the versions they use in `tests/golden.yml`. Golden tests are labelled
  and skip when data is missing on a host.
- Small fixtures cut from a dataset may be committed in the consuming repository (tier T0),
  with their source `id@version` recorded.

## Rationale

- Test data is a development aid, not a critical platform part. Its frequent changes would
  clutter the hub history.
- The data is too large to push and must stay local. A versioned catalog keeps tests
  reproducible across data changes and lets each host hold a partial cache.
- A self-contained repository is understandable and usable on its own: its README explains everything, and `python3 tools/testdata.py …` works in a plain clone. In a workspace, `muon testdata …` passes through to it (developer guide).

## Consequences

- The procedures live in `testdata/README.md`, the single place to read.
- The current datasets are placeholders (an uncurated copy from the legacy `muon400_process`
  working tree). They will be replaced by a curated selection.
- If data must later be shared across hosts or churns often, the byte storage can move to a
  content-addressed store. The `id@version` interface stays.

## Amendment 2026-10-23: several hosts

Golden bytes are host-local, so a second development host has no replay data. Until a remote store
exists, copy `golden/` with rsync, or point `MUON_DATA_ROOT` at a shared copy. `muon doctor` reports
the data root it uses. When a second host needs the data routinely (a hardening trigger, engineering process §5), add an optional
remote (NAS, rsync target or object storage) to `tools/testdata.py`, with `fetch <id>@<v>` and `publish <id>@<v>`
commands that verify against the catalog fingerprints. The `id@version` interface is unchanged.
