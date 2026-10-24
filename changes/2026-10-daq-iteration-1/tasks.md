# Tasks

Repositories after 2026-10-23 (ADR-012): DAQ is `core/daq/`; its contracts are in `core/contracts/`.

| # | Repo | Task | Spec IDs | Verification | Status |
|---|---|---|---|---|---|
| 1 | platform, core | Decide wire-protocol ownership (proposal decision 1): `daq/ref` owns it; `contracts/wire` removed | — | decision recorded in proposal | done |
| 2 | (legacy) | Archaeology of `usb_app2` and `legacy/muon400_process/src/fx3` → `as-is.md`, `golden-data.md` (skill `muon-legacy-archaeology`) | FR-001…FR-006 | user review | draft done 2026-10-23 |
| 3 | core, testdata | Golden-data plan: pick raw datasets from `testdata` (placeholders today, ADR-011), add the first recorded captures from `jw-muon-150test` as new `testdata` ids, pin them in `core/daq/tests/golden.yml` → `golden-data.md` | FR-004, FR-005 | fixtures replay | todo |
| 4 | core | `contracts/science/fsm/daq_device.yaml` from the state machine spec | FR-001 | table review; transition tests generated or checked | todo |
| 5 | core | Raw-capture format + run metadata (after decisions 2, 4, 5), including provenance and time-sync fields; `contracts/system/time/` | FR-004, FR-005, FR-011 | schema review | todo |
| 6 | core | `contracts/system/domain_service/` pattern + `contracts/science/api/` DAQ service API on top of it | FR-007 | schema review | todo |
| 7 | — | ~~Pin the new `contracts` revision in `west.yml`~~: obsolete, because contracts change together with core (ADR-012) | — | — | obsolete |
| 8 | core | Implementation following `core/daq/doc/implementation-priorities.md` | FR-001…FR-012 | `muon verify core` + hardware tests | in progress (prototype) |

## Next

- Documentation maintenance: added the ADR topic/status index and lifecycle guidance, linked the
  docs overview, and clarified ADR-010/ADR-012 relationships. DAQ review remains next; no hardware tests run.

- Documentation maintenance: removed the stale support-project `config/` entry from the legacy
  inventory; `legacy/config/` is documented under managed legacy repositories. No hardware tests run.
- Owner review of `as-is.md` (especially discrepancies D1–D14) and `golden-data.md`. Questions for the
  hardware/firmware side: D1 (op 0x05), D2 (`ram_id`), D3 (op 0x08 Filter), D9 (CRC-32/MPEG-2), D10
  (`frame_index` scope and reset), D11 (32-bit timestamp), D12 (6 chips per ADM fixed?), D13 (threshold
  semantics).
- Then task 3: approve the fixture set F1–F4 (`fx3-gen1-raw@v1`), import it, add the T0 cuts and the
  spec scanner as a test helper in `core/daq/tests/`.
- Hardware reference session on `jw-muon-150test` (golden-data §5) needs the owner.
- Open decisions 2–5 in `proposal.md` are unchanged. Decision 5 (timestamp) now has evidence: 32-bit,
  wraps about every 34.4 s.
- Hardware tests: none run (archaeology only).
