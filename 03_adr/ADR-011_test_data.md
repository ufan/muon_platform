# ADR-011 Test Data Management

Version: 1.0
Status: Accepted (2026-10-22)
Related: ADR-008 (replay), ADR-009 (workspace), ADR-010 (domain iteration, golden data)

## Decision

Test datasets (real recorded data used for testing, verification, replay and demos) are
managed by a **dedicated, self-managed repository `muon_testdata`** (west project `testdata`),
not by the platform hub.

- The repository holds only the **catalog and the tool** (`catalog.yml`, `tools/testdata.py`,
  `README.md`). The **bytes stay local** on each host, git-ignored, in a read-only data root
  (default `testdata/golden/`, override `MUON_DATA_ROOT`).
- Datasets are addressed as immutable **`<id>@<version>`**:
  - modifying a dataset creates the next version, hard-linking unchanged files;
  - deleting one marks the version retired;
  - local bytes are removed only by an explicit prune.
- Each change is one reviewed commit in `muon_testdata`. The hub tracks that repository's
  `main`, so dataset changes never touch the hub history. A frozen platform manifest still pins
  the exact catalog commit.
- Consumers **pin** the versions they use in `tests/golden.yml`. Golden tests are labelled
  and skip when data is missing on a host.
- Small fixtures cut from a dataset may be committed in the consuming repository (tier T0),
  with their source `id@version` recorded.

## Rationale

- Test data is a development aid, not a critical platform part. Its frequent changes would
  clutter the hub history.
- The data is too large to push and must stay local. A versioned catalog keeps tests
  reproducible across data changes and lets each host hold a partial cache.
- A self-contained repository is understandable and usable on its own (plain clone, no west).

## Consequences

- The procedures live in `testdata/README.md`, the single place to read.
- The current datasets are placeholders (an uncurated copy from the legacy `muon400_process`
  working tree). They will be replaced by a curated selection.
- If data must later be shared across hosts or churns often, the byte storage can move to a
  content-addressed store. The `id@version` interface stays.
