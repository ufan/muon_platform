# Decision log

Small decisions, one dated line each, newest first. Larger ones become ADRs. This file is the shared
memory of every session, AI tool and host (ADR-012 §8): if a decision matters next time, write it here.

- 2026-10-23: AI tools verified from `core/`: Claude Code, Codex, OpenCode (generated `opencode.json`) and Antigravity (`agy`; host setting `read_file(<workspace>)` + `command(muon status)` in `~/.gemini/antigravity-cli/settings.json`). Each repo's `AGENTS.md` carries a read-first block, because Codex and agy do not load `platform/AGENTS.md` from outside the git root.
- 2026-10-23: Cutover done: workspace rebuilt with `muon ws init`; `ufan/muon_daq` archived; Codex hybrid-core branches and `.migration/` deleted.
- 2026-10-23: West is no longer the workspace interface. vcs2l `.repos` files (`platform/repos/`) plus the `muon` CLI replace it; repositories may use west internally (ADR-012).
- 2026-10-23: Repository baseline: one repository per domain; `muon_core` is the scientific domain; `muon_instrument` coordinates (future); `muon_contracts` holds system contracts after the extraction trigger (ADR-012 §3, §6).
- 2026-10-23: `muon_daq` and `muon_contracts` histories live in `muon_core` (`daq/`, `contracts/`). `muon_daq` is retired after cutover; `muon_contracts` becomes a placeholder.
- 2026-10-23: Staged rigor: prototype lane by default, change proposals optional, hardening triggers in ADR-012 §6.
- 2026-10-23: Telemetry reaches reconstruction only as conditions. The edge appliance clock is the single time authority, with a budget of about 1 s; sensor controllers share no clock with the DAQ.
- 2026-10-23: Reconstruction uses gas pressure/temperature (gain), HV (good-time intervals, gain) and pose (direction/world frame).
- 2026-10-23: `config` content will be split into tiers at the start of preprocess: detector model (core), instrument assembly + deployment geometry/alignment (config, append-only versions), app settings (apps).
- 2026-10-22: The device ↔ host wire protocol is owned by `core/daq/ref/<target>/`; the old `contracts/wire/` was retired.
- 2026-10-22: `archive/` holds host-local trees (imaging, frame), recorded only in `legacy_inventory.md`; the imaging development approach is undecided.
- 2026-10-22: Maturity `reference` was renamed `support`.
- 2026-10-21: Test data lives in `muon_testdata` (catalog + tool; bytes local, read-only), referenced as `<id>@<version>` (ADR-011).
- 2026-10-21: Development is bottom-up, one domain at a time: DAQ first (rewrite from spec, legacy is reference only), then preprocess.
- 2026-10-21: GitHub (`ufan`) is the default remote; legacy and support repositories may keep gitee or other remotes.
