# Golden-data plan: DAQ (task 2 → task 3)

Status: draft for owner review (2026-10-23). ADR-010 §4 step 2, ADR-011.

## 1. What exists

The `testdata` placeholder datasets (uncurated copies of the legacy working tree) contain raw FX3
captures written by `usb_app2`. A raw capture starts with `ffab53xx`. Next to them are the legacy
chain's outputs: `*_ustcformat.dat` from the fx3 converter, per-link files starting `ac0f…`, ROOT and JSON.

| Dataset | Raw captures | Notes |
|---|---|---|
| `nankeda@v1` | 11 | 4 ADMs, cosmic, 10-min files |
| `150only@v1` | 51 | 3 ADMs, cosmic |
| `150fullsys@v1` | 971 | 3–4 ADMs, HV and gain scans (`detector1/gain0x17/…`) |
| `shentie@v1` | 855 | 3 ADMs; baseline and cosmic; assembly tests (`assembly/…`); some files start with status frames |

**Not available:**
- recordings of the **command/status exchange**, since `usb_app2` keeps only a GUI log;
- run metadata (configuration sent, thresholds, operator actions);
- any capture of fault behaviour (missing status, recovery, Stop during load).

## 2. Can legacy produce reference outputs?

- **usb_app2:** only with the hardware (PyQt GUI, Windows-oriented). It can't be run headless, so it can't produce DAQ-level outputs for comparison in CI. It is useful once on `jw-muon-150test` to record a reference session (below).
- **fx3 converter:** runs offline; it builds with C++20 + Boost, but I haven't run it. Its outputs (`*_ustcformat.dat`) already sit next to many raw files. They're a reference for **decoding** (preprocess iteration), not for DAQ.
- **Structural expectations** come from an independent scanner written to the spec (scratch script used for `as-is.md` §4). Each number is hand-checkable against the spec. Task 3 turns it into a test helper in `core/daq/tests/`.

## 3. Proposed DAQ fixtures

These become a curated dataset, proposed id `fx3-gen1-raw@v1`. It is imported with `muon testdata import` in task 3, after owner approval, and pinned in `core/daq/tests/golden.yml`.

| Fixture | Source (current placeholder path) | Size | Covers |
|---|---|---|---|
| F1 baseline, start of run | `shentie@v1 assembly/cabin_assembly/baseline/nohv/run-0.dat` | 64 MB | `ffab530f`; `frame_index` from 0; 3 leading status frames; full 128-channel chips |
| F2 cosmic, small | `150only@v1 run-30.dat` | 0.86 MB | 3 ADMs; status frame mid-stream; rotation mid-sequence |
| F3 cosmic, 4 ADMs | `150fullsys@v1 detector1/gain0x17/845v860v_3sigma_neg10sigma/run-110.dat` | 2.8 MB | 4 ADMs |
| F4 cosmic, full 10-min file | `nankeda@v1 run-1.dat` | 24 MB | 123,864 frames; 18 timestamp wraps |

Small cuts of F1 and F2 (the first ~200 frames, including the status frames) are committed in `core/daq/tests/fixtures/` as tier T0 (ADR-011). They record their source `id@version`, so unit tests run without the data root.

## 4. Expected values and tolerances

All values are exact (tolerance 0). They come from the scan on 2026-10-23.

| Fixture | Frames | ADMs | Chips/frame | Triggers per ADM | Status frames | `frame_index` | Timestamp wraps | CRC-32/MPEG-2 |
|---|---|---|---|---|---|---|---|---|
| F1 | 19,764 | 0,1,2 | 6 | 6,588 each | 3 (leading) | 0…, no gaps | 1 | all valid |
| F2 | 2,046 | 0,1,2 | 6 | 682 each | 1 | 58920…, no gaps | 17 | all valid |
| F3 | 2,560 | 0–3 | 6 | 640 each | 0 | 23292…, no gaps | 18 | all valid |
| F4 | 123,864 | 0–3 | 6 | 30,966 each | 0 | 57640…, no gaps | 18 | all valid |

The CRC check covered the first 300 frames of each of the four files; task 3 verifies every frame. In all four files, `dcm_sync == adm_sync` and `word_count = hits + 4` held for every frame.

- **Capture/replay (FR-004/005):** the rewrite's persisted data stream must be **byte-identical** to the input data frames. Status frames go to a separate status log and are excluded from the data stream (as-is D8).
- **Validation counters (FR-009):** zero CRC, continuity and sync errors on these fixtures. Corrupted copies (a flipped bit, a dropped frame, a truncated tail) must raise exactly one error of the right kind.

## 5. Hardware reference session (needs the owner, on `jw-muon-150test`)

Record one complete `usb_app2` session (`daemon-dev`) with Linux `usbmon` (pcap, e.g. `tshark -i usbmon<bus>`):
1. Check → Reg02 → Reg03 → thresholds → Th_value → mode baseline → trigger layers → Start → about 2 min → Stop;
2. then the same in cosmic mode;
3. plus one deliberate fault (unplug or reset during acquisition).

This gives the command/status golden sequence, real status timings, and one fault trace. Store it as `fx3-gen1-session@v1`, together with the GUI log and the Excel thresholds used.
