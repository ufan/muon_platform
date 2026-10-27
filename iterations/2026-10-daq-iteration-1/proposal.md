# DAQ iteration 1: fx3/gen1 acquisition service

Status: active
Owner: project owner
Affected repositories: `core` (`daq/`, `contracts/`; active); references: `legacy/usb_app2`, `legacy/muon400_process` (`src/fx3`)
Requirements: `daq:FR-001` … `daq:FR-012`

## Capabilities

Step 0 is done in `docs/architecture/system_architecture.md` §5. Archaeology and the golden-data plan
(steps 1–2) cover the whole domain; both are provisional (tasks 2 and 3). No capability has a baseline yet (`core` has no `openspec/`), so
the prototype in task 8 is exploration.

| Capability | Repository | Playbook step | Stage (§4) |
|---|---|---|---|
| Device state machine (`daq_device`) | core | 2 | exploration |
| Raw capture and run metadata | core | 2 | exploration |
| Domain-service pattern and DAQ service API | core | 2 | exploration |
| Time base and clock correlation | core | 2 | exploration |
| Raw stream to consumers | core | 2 | exploration |

## Why

DAQ is the first domain of the bottom-up rebuild (engineering process §1). Its outputs (the raw-capture
stream and the control/status API) are the inputs of every later domain.

## Approach

**Rewrite from spec** (decided 2026-10). Legacy code is a behaviour reference only:

- `jw-1404/usb_app2` (`daemon-dev` = lab hardware, `deploy` = field). This is the primary prototype reference.
- `legacy/muon400_process/src/fx3` (gitee `chinamyworld/fx3`, branch `hotfix`). This is the older FX3 readout.

Hardware source of truth: `core/daq/ref/fx3/gen1/`. DAQ's own phase plan and order are in
`core/daq/doc/roadmap.md` and `core/daq/doc/implementation-priorities.md`. This proposal does not repeat them.
It only covers the platform-level outputs of the iteration.

## Scope

In scope:
- as-is spec of the prototype's command sequencing, configuration, acquisition lifecycle and recovery;
- golden data: recorded raw captures from `jw-muon-150test` with known run conditions;
- the provisional cross-project contracts that DAQ produces:
  - raw-capture format and run/segment metadata (`contracts/persistence/`, `contracts/pipeline/`);
  - service API (`contracts/api/`);
  - device state machine as a table (`contracts/fsm/daq_device.yaml`);
- DAQ implementation following `daq/doc/implementation-priorities.md`.

Out of scope: preprocess rewrite (iteration 2), online event building beyond what `daq:FR-012` needs as a consumer interface.

## Decision requests

Classes and fields: skill `muon-domain-iteration`. Only the integrator edits this section.
Converted 2026-10-27 from the former "Decisions needed" list. Approved requests are decisions; its full wording is in git history.

| Id | Class | Capability | Decision | Recommendation | Evidence | If wrong | Confirms when | Lands in | Status |
|---|---|---|---|---|---|---|---|---|---|
| DAQ-0 | ask | all | Start DAQ iteration 1; rewrite from spec, legacy as reference only | — | `governance/decision_log.md` 2026-10-21 | — | — | — | approved — owner, human, 2026-10-21, authority: owner |
| DAQ-1 | ask | all | Wire-protocol ownership | `daq/ref/<target>/` owns the device ↔ host protocol; `contracts/wire/` removed. The data-frame schemas `daq/ref/fx3/gen1/schema/protocol.{fbs,proto}` are candidates for `contracts/pipeline/`, decided in the preprocess iteration | stale April snapshot, identical apart from one broken link | two sources of truth for the protocol | — | `core/contracts/README.md`; repository model | landed — stated in `core/contracts/README.md` and the repository model (before 2026-10-27) |
| DAQ-2 | show | raw capture | Raw-capture container format | none yet; task 5 proposes one (candidates: segmented binary + JSON sidecar, an existing container) | — | replay and provenance redone; format version bump | task 5 proposal written | `core/contracts/science/persistence/` | open |
| DAQ-3 | show | all | Clone `usb_app2` into the workspace or reference it on GitHub only | keep it cloned and locked (already `legacy/usb_app2`, `repos/legacy.repos`) | `muon status`: LOCKED | none; reversible | now | — | provisional |
| DAQ-4 | show | raw capture, time base | Raw-capture provenance and time fields (system architecture §6) | run header with `boot_id`, clock source and sync state, core SHA, conditions snapshot ID + content hash (resolved snapshot embedded); periodic clock-correlation records (device timestamp ↔ edge monotonic ↔ UTC) | runs last days; the device clock drifts and wraps (DAQ-5) | data products not traceable; time reconstruction impossible for old runs | task 5 schema written | `core/contracts/science/persistence/`, `core/contracts/system/time/` | provisional |
| DAQ-5 | show | time base | Device timestamp semantics | treat the 8 ns `timestamp` as 32-bit, wrapping about every 34.4 s; unwrap with the clock-correlation records of DAQ-4 | `as-is.md` D11: 32-bit in all four fixtures, 18 wraps in F4 | wrong unwrapping; time drift in products | firmware answer on width and on whether `Stop`/reset clears it (task 9) | `core/daq/ref/fx3/gen1/`, `core/contracts/system/time/` | provisional |
| DAQ-6 | show | raw capture | Fixture set F1–F4 as `fx3-gen1-raw@v1`, exact expected values (tolerance 0), T0 cuts of F1 and F2 | as `golden-data.md` §3–4 | scan of 2026-10-23 | tests anchored to a wrong oracle | full-frame CRC check in task 3. Approval is also the explicit request to change `testdata` (a support repository); the import itself is `ask` | `core/daq/tests/golden.yml` | provisional |
| DAQ-7 | show | device FSM | D5 status timeout | use the spec's 2 s | `as-is.md` §5 D5 | spurious or late faults | now | device FSM baseline change (core) | provisional |
| DAQ-8 | show | device FSM | D6 failure handling | spec wins: Stop → recover → reconfigure (FR-002) | `as-is.md` §5 D6 | unrecoverable runs | now | device FSM baseline change (core) | provisional |
| DAQ-9 | show | device FSM | D7 status validation | spec wins: check header, tail, op and ack bitmap | `as-is.md` §5 D7 | accepting corrupt status | now | device FSM baseline change (core) | provisional |
| DAQ-10 | show | raw capture | D8 status/data demultiplexing | demultiplex 4-byte `FA..FE` frames while acquiring; never persist them as data | `as-is.md` §5 D8; F1, F2 contain status frames | raw stream polluted; replay not byte-identical | now | raw capture baseline change (core) | provisional |
| DAQ-11 | show | raw capture | D15 data loss | never drop raw data (already in requirements) | `as-is.md` §5 D15 | silent data loss | now | raw capture baseline change (core) | provisional |
| DAQ-12 | show | raw capture | D16 frame alignment of files | the capture format must not rely on files starting on frame boundaries | `as-is.md` §5 D16 | replay breaks on split frames | now | raw capture baseline change (core) | provisional |

The hardware and firmware questions D1–D4 and D9–D14 are `blocked: external` (task 9).

## Delegation

None: the owner settles every `show` request.

## Revisions

| Date | What changed | Affected artifacts | Approvals reopened |
|---|---|---|---|

## Risks and verification impact

- The legacy chain cannot run end to end, so golden data relies on hardware captures and hand-checked expectations.
- Hardware validation is only possible on `jw-muon-150test`. Every result must state which hardware tests were run.
