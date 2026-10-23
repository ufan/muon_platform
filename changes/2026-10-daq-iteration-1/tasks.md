# Tasks

Repositories after 2026-10-23 (ADR-012): DAQ is `core/daq/`; its contracts are in `core/contracts/`.

| # | Repo | Task | Spec IDs | Verification | Status |
|---|---|---|---|---|---|
| 1 | platform, core | Decide wire-protocol ownership (proposal decision 1): `daq/ref` owns it; `contracts/wire` removed | — | decision recorded in proposal | done |
| 2 | (legacy) | Archaeology of `usb_app2` and `legacy/muon400_process/src/fx3` → `as-is.md` (skill `muon-legacy-archaeology`) | FR-001…FR-006 | user review | todo |
| 3 | core, testdata | Golden-data plan: pick raw datasets from `testdata` (placeholders today, ADR-011), add the first recorded captures from `jw-muon-150test` as new `testdata` ids, pin them in `core/daq/tests/golden.yml` → `golden-data.md` | FR-004, FR-005 | fixtures replay | todo |
| 4 | core | `contracts/science/fsm/daq_device.yaml` from the state machine spec | FR-001 | table review; transition tests generated or checked | todo |
| 5 | core | Raw-capture format + run metadata (after decisions 2, 4, 5), including provenance and time-sync fields; `contracts/system/time/` | FR-004, FR-005, FR-011 | schema review | todo |
| 6 | core | `contracts/system/domain_service/` pattern + `contracts/science/api/` DAQ service API on top of it | FR-007 | schema review | todo |
| 7 | — | ~~Pin the new `contracts` revision in `west.yml`~~: obsolete, because contracts change together with core (ADR-012) | — | — | obsolete |
| 8 | core | Implementation following `core/daq/doc/implementation-priorities.md` | FR-001…FR-012 | `muon verify core` + hardware tests | in progress (prototype) |

## Next

- Workspace reorganization (`changes/2026-10-workspace-reorg/`) is done locally and awaits push and cutover.
  After that, continue with task 2 (archaeology) or task 8 (prototype), whichever the owner prefers.
- Open questions for the owner: proposal decisions 2–5 (raw-capture format; clone `usb_app2`; provenance and
  time fields; device-timestamp width and reset).
- Hardware tests: none run since the reorganization (no DAQ behaviour changed).
