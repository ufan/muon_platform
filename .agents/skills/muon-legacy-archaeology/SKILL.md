---
name: muon-legacy-archaeology
description: Use at the start of a domain iteration to turn legacy code into an as-is spec and golden-data plan (ADR-010 §4, steps 1–2). Legacy code is read-only reference.
---

# Legacy archaeology

Inputs: the domain in scope and its rows in `platform/docs/legacy_inventory.md`.

1. Make sure the legacy references are present and locked: `west refs sync`. They are read-only on disk, with commits and pushes disabled (ADR-009 §15). Never unlock or `chmod` them. To run legacy code, build out of tree in `west refs build-dir <name>`.
2. For each legacy module, record in `<change>/as-is.md`:
   - inputs and outputs (formats, units, byte layouts, file names);
   - configuration and calibration dependencies (which `config/` files, which fields);
   - control flow and state (sequencing, timeouts, retries);
   - failure modes and how they are handled or ignored;
   - implicit knowledge (magic numbers, hardware quirks, physics assumptions), each with `repo:path:line@commit`.
3. List discrepancies with the authoritative references (e.g. `daq/ref/` for hardware). Do not resolve them silently.
4. Write a golden-data plan in `<change>/golden-data.md`:
   - which recorded inputs exist, and where;
   - whether the legacy code can produce reference outputs;
   - tolerances for comparison.

   If legacy cannot run, use recorded hardware captures plus hand-checked expectations.
5. Update `platform/docs/legacy_inventory.md` (runnability, notes).
6. Report open questions to the user.
