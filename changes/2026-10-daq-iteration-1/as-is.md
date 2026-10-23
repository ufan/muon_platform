# As-is specification: legacy DAQ (task 2)

Status: draft for owner review (2026-10-23). ADR-010 §4 step 1. Legacy code is reference only.

**Sources examined (read-only, locked):**

| Reference | Revision | What it is |
|---|---|---|
| `legacy/usb_app2`, branch `daemon-dev` | `3a00ac2` (2025-12-19) | PyQt5 operator GUI that controls the FX3/DCM and writes raw captures. Lab-hardware version. |
| `legacy/usb_app2`, branch `deploy` | `f9ba4e0` (2026-03-03) | Field version: different defaults; runs the legacy chain after every file. `deploy-device-2` is identical; `deploy-device-3` (`5659534`) changes only the device id. |
| `legacy/usb_app2`, branch `v3-dev` | `c3ecfc1` | "online recon added for windows". Not examined in detail. |
| `legacy/muon400_process/src/fx3`, branch `hotfix` | `153382e` | **Offline converter**, not a USB reader: parses a raw capture and repacks it into the "USTC format" used by the legacy chain. |
| Authoritative | `core/daq/ref/fx3/gen1/formal_protocol_spec.md` | Device ↔ host protocol (source document dated 2025-11-07/11). |
| Evidence | `testdata` raw captures (see `golden-data.md`) | Byte-level checks with an independent scanner written to the spec. |

Citations use `repo:path:lines@commit`. "Evidence" means checked against recorded raw captures.

## 1. Transport (usb_app2)

- **Device:**
  - USB VID `0x04b4` (Cypress), PID `0x00f1`; interface (0,0); bulk OUT EP `0x01`, bulk IN EP `0x81` (`usb_app2:main.py:42-45@3a00ac2`);
  - pyusb + libusb1;
  - the backend is hard-coded to load `libusb-1.0.dll`, so the GUI was written for Windows (`main.py:40`);
  - Linux access needs the udev rule `88-cyusb.rules` (VID `04b4`, mode 666).
- **One IN endpoint carries both** the 4-byte status frames and the acquisition data stream. While acquiring, the reader thread consumes everything, so late status frames end up in the raw file. Evidence: `shentie@v1 assembly/cabin_assembly/baseline/nohv/run-0.dat` starts with `fa 06 02 fe  fa 06 04 fe  fa 07 07 fe`, and `150only@v1 run-30.dat` contains one status frame mid-stream.
- **Reads:**
  - every read requests 16384 bytes;
  - command acknowledgements wait 1000 ms (300 ms for threshold data) (`main.py:834-851`, `:623`);
  - the acquisition reader waits up to 60 s per read and ignores `errno 110` timeouts (`threads.py:39-75`).
- **Writes:** one `ep_out.write` per command frame (`main.py:853-867`).

## 2. Commands (usb_app2)

Every frame is `FA <adm_select> <op_type> <op_value> [payload]` (`main.py:745-832`).

| Prototype name | Bytes / payload | Sent to | Spec meaning |
|---|---|---|---|
| `Check` | `FA FF 01 00` | all | Check link. The status `value` byte is the online-ADM bitmap, stored as `self.boards` (`main.py:716-718`) |
| `02-Reg02` | `FA <b> 02 00` + N×(`chip_id`, 24-bit value) | **one board at a time** | op 0x02 = write **REG1**. Default value `0x00ac0837` for every chip |
| `02-Reg03` | `FA <b> 03 00` + N×(`chip_id`, value) | one board at a time | op 0x03 = write **REG0**. Default `0x0080010f` |
| `03-Th_data` | `FA <b> 04 <chip> ` + 128×(`channel`, 24-bit threshold) | per board, per chip | op 0x04, but `op_value` carries the **chip index** (spec: `ram_id`) (`main.py:814-832`) |
| `05-Th_value` | `FA <b> 05 <v>` | per board; per-layer values from the GUI (`main.py:1246-1343`) | op 0x05 = **threshold count**. Default `0x07` (daemon-dev) / `0x02` (deploy) |
| `06-Th_enable (baseline/Cosmic)` | `FA <b> 06 00/01` | per board | op 0x06 acquisition mode (matches the spec) |
| `Select_Trigger_Layers` | `FA 00 81 <n>` | back-end | op 0x81 trigger layers. Default 3 (daemon-dev) / 2 (deploy) |
| `08-Filter` | `FA <b> 08 00` | per board | **not in the spec** |
| `Start` | `FA <online-bitmap> 07 01` | online boards | op 0x07 start |
| `Stop` | `FA FF 07 00` | **always broadcast** (commit `ac475a7`) | op 0x07 stop |

- **N, the number of register entries,** is `chips_per_board`, selectable as 6/16/24. The default is **24** on `daemon-dev` and **6** on `deploy` (`main.py:145-163`; deploy diff). The evidence shows **6 chips per ADM** in every capture.
- **Status handling:**
  - only the length is checked (`readed != 4`); header `FA`, tail `FE`, `return_op_type` and the acknowledgement bitmap are never validated;
  - after each command the prototype sleeps 0.1 s;
  - on a bad or missing status it logs, shows a dialog and **aborts the sequence**: no Stop, no retry, no reconfiguration;
  - `Stop` in the command path does not wait for its status; it starts the stop/drain sequence (`main.py:704-707`).

## 3. Control flow and state (usb_app2)

The operator drives everything by hand. There is no explicit state machine; flags `is_running` / `is_stopping` and Qt timers stand in for one.

1. **Connect:** `set_configuration`, find the endpoints (`main.py:434-465`).
2. **`Check`** gives the online-ADM bitmap and the layer indicators.
3. **Registers:** `02-Reg02`, `02-Reg03` per board. Check prints a reminder to send these manually (`main.py:722`).
4. **Thresholds:** load the Excel threshold file (`main.py:1105-1224`), then `03-Th_data` per board and chip.
5. **`05-Th_value`** per board.
6. **Mode:** `06-Th_enable` (baseline or cosmic) per board. This sets `collection_mode` on the host too.
7. **`Select_Trigger_Layers`.**
8. **`Start`:**
   - reads its status;
   - creates the directory `<data_dir>/<YYYYmmdd_HHMM>/`;
   - starts `UsbReaderThread` and a `FileWriterThread` writing `<run_prefix>-<n>.dat`;
   - starts a 1 s timer (`main.py:890-940`).
9. **Rotation:** every `file_interval_minutes` (10 on daemon-dev, 2 on deploy) the writer is replaced and a new file opened. No command is sent to the device, so acquisition continues (`main.py:1356-1390`).
10. **`Stop`:** broadcast Stop, sleep 0.5 s, stop the reader, then drain the IN endpoint: 16 KB reads with a 1 s timeout until 20 consecutive empty reads, about 20 s (`main.py:989-1041`, `threads.py:139-178`).

**Recovery (`复位 USB`, `main.py:1589-1685`):**
- broadcast Stop, `clear_halt` both endpoints, dispose resources;
- poll up to 15 s for the device to re-enumerate, `set_configuration`, drain;
- then it claims to "auto Start" but sends `FA FF 06 00`, i.e. **set baseline mode**, not Start (bug);
- `old_dev.reset()` is called after `old_dev = None`, so the USB reset never happens (bug).

**Persistence (`threads.py:82-137`):**
- raw USB payloads are concatenated with no header, run metadata, checksum or index;
- writes are batched to 2 MB, or flushed every 2 s;
- no fsync.

**Data loss:**
- the reader queue holds 20,000 packets; when full, packets are **dropped** with only a log line (`threads.py:54-58`);
- on stop, the writer's final batch is reopened in append mode, so ordering is preserved, but nothing reports loss.

**Deploy-only:**
- after each file the writer runs the legacy chain twice: `online/bin/data_process.sh -p -i 120 -I 2 -r 1 -b <start_ms> -c online/config -d <file> -L 0x7 -m 40 -k 3 -M -K tracks`, then the same with `-k 2 -UDFPHM -K tracks_2` (`threads.py` deploy diff);
- here `-p` pushes tracks to a database, `-I` is the device id, `-b` the acquisition start in epoch ms, and `-c` the config directory (now `legacy/config`).

So in the field, DAQ, preprocess and recon are coupled per file through a shell script.

## 4. Data format: what the evidence shows

The spec is right about the frame layout. Checks on four datasets (section 6) settle what it leaves open:

| Item | Evidence | Spec says |
|---|---|---|
| Byte order | big-endian throughout | same |
| CRC word (`N+3`) | **CRC-32/MPEG-2** (poly `0x04C11DB7`, init `0xFFFFFFFF`, no reflection, no final XOR) over the USB frame from DW1 (`ffab53xx`) through the `ffcc0000` trailer inclusive. 300/300 frames matched in each file checked | "CRC check word", no algorithm |
| `frame_index` | **one DCM-wide counter** across all ADMs; continuous (0 gaps in 123,864 frames); **resets to 0 at Start** (baseline files start at 0); continues across file rotation | continuous, starts from 0 |
| Device timestamp | **32-bit**, shared by all ADMs (identical deltas), 8 ns units, **wraps every 2³²×8 ns ≈ 34.36 s** (17–18 wraps in a 10-min file) | "8 ns units" |
| `dcm_sync_id` vs `adm_sync_id` | always equal | `adm_sync_id` is the sampling cycle |
| Chip `word_count` (`ee`) | always **hits + 4** (temperature word + 3 trailer words) | `word_count`, undefined |
| Chip word 1 | `00 0A <temp16>`: the 16-bit field before the temperature is always `0x000A` | `yy = 0x0A` |
| Chips per ADM frame | 6 in every capture | chips 0..5 in the register config |
| Hits per chip | cosmic: zero-suppressed; baseline (`ffab530f`): all 128 channels (`ee = 0x84`) | non-hit channels compressed out |
| Event layout | each trigger: one frame per online ADM, **adjacent** in the stream, never interleaved; all online ADMs report every trigger; the last event at a stop or rotation boundary may be incomplete | aggregate by `trigger_id`; frames not ordered by `adm_index` |
| Zero padding after `fffeaaaa` | none seen (the Python parser tolerates it) | none |
| Status frames in the data stream | present (section 1) | not addressed |

Physics and hardware constants used by the legacy code:
- **Temperature:** `T[°C] = (raw − 0x5DAC)/80 + 25` (`fx3:inc/unpack.h:50-55@153382e`).
- **Voltage test:** `V = (end0 & 0xFFFF) × 28.924e-6 + 0.602` (`unpack.h:56`).
- **ADC:** 24-bit; baseline offset **`0x4000` (16384)**.
- **Thresholds:** `floor(mean + kσ) − 0x4000`, clipped to ≥0, and values above `0x3000` are replaced by `0x4000` (treated as EMI, which masks the channel). This is on `deploy`. `daemon-dev` uses `floor(0x4000 − kσ)` ("absolute threshold", negative k allowed). k defaults to 3 per layer (`analysis.py` on both branches).
- **Channel key:** `fec(3) | chip(5) | channel(8)` (`threads.py:190-198`).

## 5. Discrepancies with the authoritative references

None of these is resolved here; they need owner or hardware decisions.

| # | Topic | Legacy | Spec / evidence | Question |
|---|---|---|---|---|
| D1 | op 0x05 | "Th_value", 0x07 / 0x02 | "threshold count" | Same thing? What are valid values? |
| D2 | op 0x04 `op_value` | chip index | `ram_id` | Is `ram_id` the chip index, or a separate RAM selector? |
| D3 | op 0x08 "Filter" | sent per board, value 0 | not defined | Does firmware implement it? Keep or drop? |
| D4 | Register naming | `02-Reg02`→op 0x02, `02-Reg03`→op 0x03 | 0x02=REG1, 0x03=REG0 | Confirm default values and their meaning |
| D5 | Status timeout | 1000 ms (300 ms for thresholds) | 0..2 s | Use the spec's 2 s? |
| D6 | Failure handling | abort sequence | Stop → recover → reconfigure | Spec wins (FR-002) |
| D7 | Status validation | length only | header/tail/op/ack bitmap | Spec wins |
| D8 | Status/data demultiplexing | none (status lands in raw files) | not specified | Specify: demultiplex 4-byte `FA..FE` frames while acquiring; never persist them as data |
| D9 | CRC | ignored | evidence: CRC-32/MPEG-2 | Confirm with firmware and add to the spec |
| D10 | `frame_index` | never checked | evidence: DCM-wide, reset at Start | Confirm, add to the spec, check continuity (FR-009) |
| D11 | Timestamp width | 32-bit read | evidence: 32-bit, wraps ~34 s | Confirm; affects ADR-012 §9 clock-correlation design (DAQ decision 5) |
| D12 | Chips per ADM | default 24 / 6 / fixed 6 | evidence: 6 | Is 6 fixed for gen1, or does it vary by ADM variant? |
| D13 | Threshold algorithm | branches disagree (relative vs absolute) | — | Which one does the firmware expect? (affects baseline tooling, not DAQ) |
| D14 | Stop scope | broadcast `FF` | `adm_select` selects boards | Always broadcast? |
| D15 | Data loss | silent drop when queue is full | DAQ integrity (FR-004/006) | Rewrite never drops raw data (already in requirements) |
| D16 | Frame alignment of files | files start on frame boundaries in the evidence | — | Capture format must not rely on it |
| D17 | Recovery bugs | "auto Start" sends `06 00`; USB reset not executed | — | Lesson only |
| D18 | Threshold file | Excel command rows `04-Th_value`, `05-Th_enable`, `03-Th_config` are silently not sent; header written for 3 layers only | — | Replace the Excel format (preprocess/conditions) |
| D19 | Trigger-layer GUI | options 7 and 8 map to `0x01` | — | Lesson only |
| D20 | fx3 converter | start tag effectively unchecked (`uint16(tag>>8)` compared with `0xffab`), 6 chips hard-coded, CRC and continuity ignored | — | Preprocess iteration |

## 6. What the rewrite should take from this

These are candidates for the spec deltas in DAQ iteration step 3. They are not decided.
- Treat the IN endpoint as a mixed stream: a framing layer separates status frames from `ffab53xx` USB frames. That way command handling works during acquisition, and raw captures hold only data. Optionally keep status frames in a separate log.
- Validate per frame: sentinels, the length relation, CRC-32/MPEG-2, global `frame_index` continuity, and `dcm_sync == adm_sync`. Count violations (FR-009) without stopping capture.
- Unwrap the 32-bit timestamp, and record clock-correlation samples (ADR-012 §9).
- Keep the operator sequence of section 3 as the configuration recipe, but make it state-machine driven, with spec-conformant status handling and recovery.
- Rotate files at frame boundaries, and add run/segment metadata and checksums (FR-004).
