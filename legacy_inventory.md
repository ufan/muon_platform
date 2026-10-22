# Legacy Inventory

Status: living document (ADR-010 §5). Last full scan: 2026-10-21.

Legacy code is a **reference only**: a source of domain knowledge and golden
data, never a dependency of new code. All legacy references live in `legacy/<dir>`,
are named `<dir>-legacy` in the manifests, and are locked read-only on disk with
commits and pushes disabled (`west refs sync` / `muon-ws refs sync`; ADR-009 §5, §15). During each domain iteration, the
"legacy archaeology" step turns the relevant entries below into an as-is spec.

Runnability: the legacy chain (fx3 readout → preprocess → analysis) cannot
currently run end to end. Details to be added by the owner.

## West projects (group `legacy`)

| Project / path | Remote | What it is | Reference for | Runnable |
|---|---|---|---|---|
| `legacy/usb_app2` (`usb-app2-legacy`; `jw-1404/usb_app2`, branches `daemon-dev` = lab hardware, `deploy` = field; declared by daq) | github jw-1404 | prototype DAQ software tested on the current hardware; not cloned in the workspace yet | **DAQ iteration 1**: command sequencing, configuration, acquisition lifecycle, recovery (see `daq/doc/guides/prototype-reference.md`) | on `jw-muon-150test` |
| `legacy/muon400_process/` (`muon400-process-legacy`, branch `deploy`) | gitee | C++ offline chain for MUON400 | DAQ (fx3), preprocess, recon | unknown |
| ├ `src/fx3` (submodule `chinamyworld/fx3`, branch `hotfix`) | gitee | FX3 USB readout host program | **DAQ iteration 1**: transport, framing, device commands | unknown |
| ├ `src/usb_data_separate` | | split the USB stream by board/link | preprocess | unknown |
| ├ `src/adas_data_unpack`, `src/adas_data_decode` | | ADAS chip frame unpack and decode | preprocess | unknown |
| ├ `src/adas_muxbrd_fit` | | multiplexed-board signal fit | preprocess / recon boundary | unknown |
| ├ `src/hit_position_reconstruct` | | hit positions from strips | recon | unknown |
| ├ `src/track_seek` | | track finding and fit, JSON output | recon | unknown |
| └ `src/scripts/data_process.sh` | | chain driver script | chain wiring, file conventions | unknown |
| `legacy/analysis/` (`analysis-legacy`) | gitee | ROOT macros, notebooks, baseline studies, plots | analysis, calibration (baselines), mapping | partial |

## Host-local references (this host only; not west projects)

Not in any manifest, so `muon-ws` neither fetches nor locks them (no L1). The
read-only rule in `AGENTS.md` (L2) still applies. Other workspaces do not have them.

| Path | What it is | Reference for | Notes |
|---|---|---|---|
| `legacy/imaging/` | git repo without a remote: research imaging pipeline scripts (`legacy/0_geology…4_convertion`, `pipe_search`, rotation helpers); tracks a 185.6 MB CSV | imaging | uncommitted work left as is (2026-10-22); how the imaging package will be developed is undecided |
| `legacy/frame/` | not git: C++/Eigen coordinate-frame library (inclinometer/detector/site/world frames, ray transforms, angle-map reprojection) | conditions (geometry/pose), imaging | |

## Test data

The datasets that used to sit untracked in `legacy/muon400_process/data/` now belong to
the `testdata` project (`muon_testdata`, ADR-011) as placeholder versions.

## Reference projects (not legacy, used as data or tools)

| Project | What it is | Future home |
|---|---|---|
| `config/` (branch `dev`) | per-site detector configs: channel and link mapping, alignment, rotation, z positions, hit ranges, `system.json` | `conditions` project |
| `tools/muon_tools`, `tools/rate_estimate` | ADC level tool, rate estimation | tools / simulation |
| `study/` | studies and timeline | research |

## Known duplication to resolve

- Rotation and frame helpers exist in `legacy/frame/rotation_util.hpp`,
  `legacy/analysis/rotation.hpp`, and `legacy/imaging/rotation_{eigen,root}.hpp`.
  These are candidates for a single geometry/frames component in `conditions`.
