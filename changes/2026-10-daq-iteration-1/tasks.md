# Tasks

| # | Project | Task | Spec IDs | Verification | Status |
|---|---|---|---|---|---|
| 1 | hub | Decide wire-protocol ownership (proposal decision 1) | — | decision recorded here | todo |
| 2 | (reference) | Archaeology of `usb_app2` and `legacy/muon400_process/src/fx3` → `as-is.md` (skill `muon-legacy-archaeology`) | FR-001…FR-006 | user review | todo |
| 3 | daq, testdata | Golden-data plan: pick raw datasets from `testdata` (placeholders today, ADR-011), add first recorded captures from `jw-muon-150test` as new `testdata` ids, pin in `daq/tests/golden.yml` → `golden-data.md` | FR-004, FR-005 | fixtures replay | todo |
| 4 | contracts | `fsm/daq_device.yaml` from the state machine spec | FR-001 | table review; transition tests generated or checked | todo |
| 5 | contracts | Raw-capture format + run metadata (after decision 2) | FR-004, FR-005, FR-011 | schema review | todo |
| 6 | contracts | Service API contract | FR-007 | schema review | todo |
| 7 | hub | Pin the new `contracts` revision in `west.yml` (skill `muon-bump-manifest`) | — | `west verify -g online` | todo |
| 8 | daq | Implementation following `daq/doc/implementation-priorities.md` | FR-001…FR-012 | `west verify daq` + hardware tests | in progress (prototype) |
