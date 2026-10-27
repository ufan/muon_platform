# Tasks

Repositories after 2026-10-23 (ADR-015, repository model): DAQ is `core/daq/`; its contracts are in `core/contracts/`.
Statuses: `todo | draft | provisional | blocked: owner | blocked: external | done`. DAQ-n ids are decision requests in `proposal.md` `## Decision requests`.

| # | Repo | Task | Spec IDs | Verification | Status |
|---|---|---|---|---|---|
| 1 | platform, core | Decide wire-protocol ownership (DAQ-1): `daq/ref` owns it; `contracts/wire` removed | — | decision recorded in proposal | done |
| 2 | (legacy) | Archaeology of `usb_app2` and `legacy/muon400_process/src/fx3` → `as-is.md`, `golden-data.md` (skill `muon-legacy-archaeology`) | daq:FR-001…daq:FR-006 | reviewer check; owner settles DAQ-7 … DAQ-12 | provisional (2026-10-23) |
| 3 | core, testdata | Golden-data plan: pick raw datasets from `testdata` (placeholders today, ADR-011), add the first recorded captures from `jw-muon-150test` as new `testdata` ids, pin them in `core/daq/tests/golden.yml` → `golden-data.md` | daq:FR-004, daq:FR-005 | fixtures replay | todo, ready up to the import (DAQ-6 provisional; import is `ask`) |
| 4 | core | `contracts/science/fsm/daq_device.yaml` from the state machine spec | daq:FR-001 | table review; transition tests generated or checked | todo |
| 5 | core | Raw-capture format + run metadata (proposes DAQ-2; builds on provisional DAQ-4 and DAQ-5), including provenance and time-sync fields; `contracts/system/time/` | daq:FR-004, daq:FR-005, daq:FR-011 | schema review | todo |
| 6 | core | `contracts/system/domain_service/` pattern + `contracts/science/api/` DAQ service API on top of it | daq:FR-007 | schema review | todo |
| 7 | — | ~~Pin the new `contracts` revision in `west.yml`~~: obsolete, because contracts change together with core (engineering process §4) | — | — | obsolete |
| 8 | core | Implementation following `core/daq/doc/implementation-priorities.md` | daq:FR-001…daq:FR-012 | `muon verify core` + hardware tests | draft (exploration prototype) |
| 9 | (external) | Hardware/firmware answers to `as-is.md` D1–D4, D9–D14; record them in `core/daq/ref/fx3/gen1/` | daq:FR-001…daq:FR-006 | answers recorded | blocked: external |
| 10 | core, testdata | Hardware reference session on `jw-muon-150test` (`golden-data.md` §5) → `fx3-gen1-session@v1` | daq:FR-001, daq:FR-002 | session recorded | blocked: owner (hardware access) |
| 11 | core | Set up `core/openspec/` from `platform/templates/project/openspec/` (`openspec init`; `openspec/config.yaml` with core's placeholders), needed before any baseline change (step 3) | — | `openspec validate --all --strict`; `muon verify core` | todo |

## Next

- Owner: one pass over the provisional requests DAQ-3 … DAQ-12 in `proposal.md` (DAQ-6 is the
  fixture set F1–F4; DAQ-7 … DAQ-12 the as-is discrepancies that need no external answer).
- Agents, without waiting: task 11 (OpenSpec in core), task 3 up to the import (T0 cuts, spec scanner as a test helper in
  `core/daq/tests/`, `golden.yml` with the exact values), and task 4 on a task branch. The import
  into `testdata/golden` waits for DAQ-6.
- External (task 9): questions D1, D2, D3, D4, D9, D10, D11, D12, D13, D14 for the hardware/firmware side.
- Owner with hardware (task 10): reference session on `jw-muon-150test`.
- Hardware tests: none run (archaeology only).
