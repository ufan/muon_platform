---
name: muon-legacy-archaeology
description: Use at the start of a domain iteration to turn legacy code into an as-is spec and golden-data plan (engineering process §1, steps 1–2). Legacy code is read-only reference.
---

# Legacy archaeology

Inputs: the domain in scope and its rows in `platform/docs/legacy_inventory.md`.

1. Make sure the legacy references are present and locked: `muon ws sync --legacy`, then `muon legacy status`. They are read-only on disk, with commits and pushes disabled (engineering process §6). Never unlock or `chmod` them. To run legacy code, build out of tree in `muon legacy build-dir <name>`.
2. List the sources examined (repository, path, commit) at the top of `<iteration>/as-is.md`. For each
   legacy module, record, keeping **observed** behaviour (cited) apart from **assumed** behaviour:
   - inputs and outputs (formats, units, byte layouts, file names);
   - configuration and calibration dependencies (which `config/` files, which fields);
   - control flow and state (sequencing, timeouts, retries);
   - failure modes and how they are handled or ignored;
   - implicit knowledge (magic numbers, hardware quirks, physics assumptions), each with `repo:path:line@commit`.
3. List discrepancies with the authoritative references (e.g. `core/daq/ref/` for hardware). Do not resolve them silently:
   each becomes a `show` decision request in the iteration's proposal (with a recommendation), or a
   `blocked: external` item when only the hardware or firmware side can answer.
4. Write a golden-data plan in `<iteration>/golden-data.md`:
   - which recorded inputs exist, and where;
   - whether the legacy code can produce reference outputs;
   - tolerances per quantity, in a form a test can read (`tests/golden.yml`).

   Fixture selection and tolerances are `show` decision requests; importing into `testdata/golden` is `ask`.

   If legacy cannot run, use recorded hardware captures plus hand-checked expectations.
5. Update `platform/docs/legacy_inventory.md` (runnability, notes).
6. Report open questions to the user.
