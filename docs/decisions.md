# Decision log

Status: current (decision log).

Small decisions, one dated line each, newest first. Larger ones become ADRs. This file is the shared
memory of every session, AI tool and host (ADR-012 §8): if a decision matters next time, write it here.

- 2026-10-24: Every platform document declares a status (`current`, `draft`, `proposed`, `reference`, `historical`; ADRs keep their own). Authority comes from declared scope, status and explicit supersession, never from specificity or ADR number; `docs/README.md` holds the convention and a guide index. Repository-local decision records are qualified outside their repository (`daq:ADR-006`). Management-bus requirement IDs renamed `FR-0n`→`IMB-00n`, `NFR-0n`→`IMB-10n` (ADR-010 §7).
- 2026-10-24: Consolidate overlapping system/platform architecture into `system_architecture.md`, retaining `platform_architecture.md` only as a compatibility pointer. The architecture index separates overview, system design and repository ownership; unresolved source discrepancies are explicit in system architecture §10.
- 2026-10-24: Architecture documents use lowercase filenames; `architecture_overview.md` replaces `LANDSCAPE.md`. The overview describes technical boundaries; work discovery and task records own iteration activity.
- 2026-10-24: `docs/architecture/repository_model.md` is the current repository-boundary and dependency entry point linked from `AGENTS.md`; ADR-012 retains decision rationale. This consolidates existing rules without changing boundaries.
- 2026-10-24: Separate stable agent rules from iteration state: `work/index.yml` supports multiple active iterations; explicit scoped assignments take priority, discussion needs no writes, and workers hand off to an integrator. Recorded in ADR-013, partly superseding ADR-012 §8; the index is discovery only, not an autonomous claim queue.
- 2026-10-24: Keep stable chronological ADR IDs and paths; navigate by a topic/status index, record explicit reciprocal supersession links, and maintain current guidance alongside decision history.
- 2026-10-24: Agent reading path is explicit in `AGENTS.md`: relevant current architecture and component spec, then linked ADRs; respect explicit supersession and flag unresolved conflicts.

- 2026-10-23: `muon_config` is a legacy repository (read by `legacy/muon400_process`): moved to `legacy/config`, read-only, `informs: [core]`. A new conditions payload repository will be created at the start of preprocess, seeded from it.
- 2026-10-23: The launcher is published on PyPI as `muon-workspace` (`tools/muon-workspace`, tag `muon-workspace-v*`, trusted publishing); the implementation is never published.
- 2026-10-23: `muon` split into a global launcher (`tools/muon-workspace`, no dependencies) and the workspace-pinned implementation (`tools/muon`); per-workspace settings in `.muon/workspace.yml` (ADR-012 §5).
- 2026-10-23: AI tools verified from `core/`: Claude Code, Codex, OpenCode (generated `opencode.json`) and Antigravity (`agy`; host setting `read_file(<workspace>)` + `command(muon status)` in `~/.gemini/antigravity-cli/settings.json`). Each repo's `AGENTS.md` carries a read-first block, because Codex and agy do not load `platform/AGENTS.md` from outside the git root.
- 2026-10-23: Cutover done: workspace rebuilt with `muon ws init`; `ufan/muon_daq` archived; Codex hybrid-core branches and `.migration/` deleted.
- 2026-10-23: West is no longer the workspace interface. vcs2l `.repos` files (`platform/repos/`) plus the `muon` CLI replace it; repositories may use west internally (ADR-012).
- 2026-10-23: Repository baseline: one repository per domain; `muon_core` is the scientific domain; `muon_instrument` coordinates (future); `muon_contracts` holds system contracts after the extraction trigger (ADR-012 §3, §6).
- 2026-10-23: `muon_daq` and `muon_contracts` histories live in `muon_core` (`daq/`, `contracts/`). `muon_daq` is retired after cutover; `muon_contracts` becomes a placeholder.
- 2026-10-23: Staged rigor: prototype lane by default, change proposals optional, hardening triggers in ADR-012 §6.
- 2026-10-23: Telemetry reaches reconstruction only as conditions. The edge appliance clock is the single time authority, with a budget of about 1 s; sensor controllers share no clock with the DAQ.
- 2026-10-23: Reconstruction uses gas pressure/temperature (gain), HV (good-time intervals, gain) and pose (direction/world frame).
- 2026-10-23: The legacy `config` content will be split into tiers at the start of preprocess: detector model (core), instrument assembly + deployment geometry/alignment (new conditions payload repository, append-only versions), app settings (apps).
- 2026-10-22: The device ↔ host wire protocol is owned by `core/daq/ref/<target>/`; the old `contracts/wire/` was retired.
- 2026-10-22: `archive/` holds host-local trees (imaging, frame), recorded only in `legacy_inventory.md`; the imaging development approach is undecided.
- 2026-10-22: Maturity `reference` was renamed `support`.
- 2026-10-21: Test data lives in `muon_testdata` (catalog + tool; bytes local, read-only), referenced as `<id>@<version>` (ADR-011).
- 2026-10-21: Development is bottom-up, one domain at a time: DAQ first (rewrite from spec, legacy is reference only), then preprocess.
- 2026-10-21: GitHub (`ufan`) is the default remote; legacy and support repositories may keep gitee or other remotes.
