# DAQ iteration 1: fx3/gen1 acquisition service

Status: draft
Playbook step: 1 (legacy archaeology). Step 0 is done in `docs/architecture/architecture_overview.md`.
Owner: project owner
Affected repositories: `core` (`daq/`, `contracts/`; active); references: `legacy/usb_app2`, `legacy/muon400_process` (`src/fx3`)
Requirements: `daq:FR-001` … `daq:FR-012`

## Why

DAQ is the first domain of the bottom-up rebuild (ADR-010). Its outputs (the raw-capture
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

## Decisions needed (human)

1. ~~**Wire-protocol ownership.**~~ **Decided 2026-10-22:** `daq/ref/<target>/` owns the
   device ↔ host protocol. `contracts/wire/` was a stale April snapshot (identical to
   `daq/ref/fx3/gen1` apart from one broken link) and has been removed, including its Chinese
   translation. The data-frame schemas `daq/ref/fx3/gen1/schema/protocol.{fbs,proto}` are
   candidates for `contracts/pipeline/` (decide in the preprocess iteration).
   `contracts/` keeps the boundaries between repositories.
2. Raw-capture container format, e.g. plain segmented binary + JSON sidecar vs. an existing container.
3. Whether to clone `usb_app2` into the workspace (`muon ws sync --legacy`: cloned and locked read-only) or reference it on GitHub only.
4. **Raw-capture provenance and time fields** (ADR-012 §9–§10). Recommended: a run header with `boot_id`,
   clock source and sync state, core SHA, and conditions snapshot ID + content hash (the resolved snapshot
   embedded); periodic **clock-correlation records** in the stream (device timestamp ↔ edge monotonic ↔ UTC),
   because runs last days and the device clock drifts and wraps.
5. **Device timestamp semantics** (ask the hardware side): the width of the 8 ns `timestamp` word (32 bits would wrap
   every ~34 s), and whether `Stop`/reset clears it. Record the answer in `core/daq/ref/fx3/gen1/`.

## Risks and verification impact

- The legacy chain cannot run end to end, so golden data relies on hardware captures and hand-checked expectations.
- Hardware validation is only possible on `jw-muon-150test`. Every result must state which hardware tests were run.
