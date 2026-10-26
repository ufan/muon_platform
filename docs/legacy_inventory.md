# Legacy Inventory

Status: current; living document ([engineering process §6](workflow/engineering_process.md#6-repositories-and-workspace)). Last full scan: 2026-10-22; DAQ archaeology 2026-10-23.

Old code and data are kept **only to inform** new work: a source of domain knowledge and
golden data, never a dependency of new code. During each domain iteration, the
"legacy archaeology" step turns the relevant entries below into an as-is spec.

There are two kinds, kept in two directories ([engineering process §6](workflow/engineering_process.md#6-repositories-and-workspace)):

| Kind | Directory | Declared in a manifest | Reproducible elsewhere | Read-only protection |
|---|---|---|---|---|
| **Legacy** (managed) | `legacy/<dir>` | yes: `platform/repos/legacy.repos`, with `informs: [...]` | yes (`muon ws sync --legacy`) | L1 on disk + L2 rules |
| **Archive** (host-local) | `archive/<dir>` | no | no: this host only | L2 rules only |

Runnability: the legacy chain (fx3 readout → preprocess → analysis) cannot
currently run end to end. Details to be added by the owner.

## Legacy (managed, `platform/repos/legacy.repos`)

List and state: `muon legacy status`. Fetch and lock: `muon ws sync --legacy`. All of them inform `core`.

| Project / path | Remote | What it is | Informs | Runnable |
|---|---|---|---|---|
| `legacy/usb_app2` (`jw-1404/usb_app2`; `daemon-dev` = lab hardware `3a00ac2`, `deploy` = field `f9ba4e0`, also `deploy-device-2/3`, `v3-dev`) | github jw-1404 | PyQt5 operator GUI: FX3/DCM control, raw capture to `<prefix>-<n>.dat`, threshold tooling; `deploy` runs the legacy chain after every file | **DAQ iteration 1**: as-is spec in `changes/2026-10-daq-iteration-1/as-is.md` | needs hardware; Windows-oriented (libusb dll); not headless |
| `legacy/muon400_process/` (branch `deploy`) | gitee | C++ offline chain for MUON400 | DAQ (fx3), preprocess, recon | unknown |
| ├ `src/fx3` (submodule `chinamyworld/fx3`, branch `hotfix` `153382e`) | gitee | **offline converter**: raw FX3 capture → "USTC format" 4096-byte packages for the chain (not a USB reader) | preprocess (decode); DAQ as-is §4/D20 | builds (C++20, Boost), not run |
| ├ `src/usb_data_separate` | | split the USB stream by board/link | preprocess | unknown |
| ├ `src/adas_data_unpack`, `src/adas_data_decode` | | ADAS chip frame unpack and decode | preprocess | unknown |
| ├ `src/adas_muxbrd_fit` | | multiplexed-board signal fit | preprocess / recon boundary | unknown |
| ├ `src/hit_position_reconstruct` | | hit positions from strips | recon | unknown |
| ├ `src/track_seek` | | track finding and fit, JSON output | recon | unknown |
| └ `src/scripts/data_process.sh` | | chain driver script | chain wiring, file conventions | unknown |
| `legacy/analysis/` | gitee | ROOT macros, notebooks, baseline studies, plots; untracked `data/` (2.2 GB gain/baseline runs) | analysis, calibration (baselines), mapping | partial |
| `legacy/config/` (`chinamyworld/muon_config`, branch `dev`) | gitee | detector/site parameter files per setup (`150test`, `400test`, `liaoda`, `nankeda`, `shentie`, `150demo`): channel/link mapping, layer geometry, z positions, rotation, alignment, hit ranges, `system.json` | conditions (core): the tier split at the start of preprocess; read by `legacy/muon400_process` via `CONFIG_PATH` | data only |

## Archive (host-local, this host only)

Not in any `.repos` file, so `muon` neither fetches nor locks them. The read-only rule in
`AGENTS.md` (L2) still applies. Other workspaces do not have them.

| Path | What it is | Informs | Notes |
|---|---|---|---|
| `archive/imaging/` | git repo without a remote: research imaging pipeline scripts (`legacy/0_geology…4_convertion`, `pipe_search`, rotation helpers); tracks a 185.6 MB CSV | imaging | uncommitted work left as is (2026-10-22); how the imaging package will be developed is undecided |
| `archive/frame/` | not git: C++/Eigen coordinate-frame library (inclinometer/detector/site/world frames, ray transforms, angle-map reprojection) | conditions (geometry/pose), imaging | |

## Test data

The datasets that used to sit untracked in `legacy/muon400_process/data/` now belong to
the `testdata` project (`muon_testdata`, ADR-011) as placeholder versions.

## Support projects (maturity `support`: used as data or tools, not legacy)

| Project | What it is | Future home |
|---|---|---|
| `tools/muon_tools`, `tools/rate_estimate` | ADC level tool, rate estimation | tools |
| `study/` | studies and timeline | research |
| `testdata/` | versioned test datasets (ADR-011) | — |

## Known duplication to resolve

- Rotation and frame helpers exist in `archive/frame/rotation_util.hpp`,
  `legacy/analysis/rotation.hpp`, and `archive/imaging/rotation_{eigen,root}.hpp`.
  These are candidates for a single geometry/frames component in `conditions`.
