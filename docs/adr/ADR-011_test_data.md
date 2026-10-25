# ADR-011 Test data

Status: Accepted (2026-10-22; re-baselined 2026-10-25 with the multi-host amendment)

## Decision

- Test datasets are managed by the repository `muon_testdata` (`testdata/`). It holds only the
  catalog and its tool; the bytes stay local and git-ignored in a read-only data root
  (`testdata/golden/`, or `MUON_DATA_ROOT`).
- Datasets are immutable `<id>@<version>`. A change creates a new version (unchanged files are
  hard-linked); deletion retires a version; bytes are removed only by an explicit prune.
- Consumers pin versions in `tests/golden.yml`; golden tests skip when data is missing. Small
  fixtures may be committed in the consumer with their source `id@version`.
- Until a remote store exists, other hosts copy the data root (rsync) or share one. When a second
  host needs data routinely, add `fetch`/`publish` to a remote store with fingerprint checks; the
  `id@version` interface stays.

## Why

The data is too large to push and changes often; a versioned catalog keeps tests reproducible and
keeps data churn out of the platform history.

## Consequences

- Procedures live in `testdata/README.md`. Current datasets are uncurated placeholders from legacy.
