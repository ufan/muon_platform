---
name: muon-promote
description: Use when content from a note or brainstorm (platform/docs/notes/ or similar) should become formal architecture, requirements, ADRs, component specs or contracts, and at domain iteration steps 0 and 3 to harvest proposed notes for that domain.
---

# Promote note content

A note is never rewritten in place into a baseline. Its binding content is restated in the
owning documents, and the note becomes a record that maps every section to its new home.

1. **Find sources.** List the `proposed` notes in the `platform/docs/README.md` notes index (and any
   notes in the affected repositories) that touch the domain or topic. Read each source fully.
2. **Find existing homes.** Read the current architecture, requirements, ADRs, component specs and
   contracts the content would land in, so you add to them instead of duplicating or contradicting them.
3. **Classify every section** of the source. Destinations follow the specification layers (engineering process §2)
   and the repository model (component content goes to the owning repository, not to platform):

   | Kind of content | Destination | Label |
   |---|---|---|
   | Required behaviour, acceptance | component spec (`<repo>/…/SPEC.md`, `specs/`) or `platform/docs/requirements/` with an ID (engineering process §3) | normative |
   | Boundary, ownership, data flow | `platform/docs/architecture/` | current |
   | Consequential choice with alternatives | new ADR (owner decides) | proposed until accepted |
   | Small agreed decision | `platform/governance/decisions.md` | — |
   | Record or message fields | `contracts/…` README or schema | proposed until frozen |
   | Plausible but undecided rule | the owning spec, marked "proposed default (not yet decided)" | proposed |
   | Useful design detail | "Reference design (non-normative)" section of the owning spec | non-normative |
   | Unresolved question or conflict | open-points list of the owning spec or system architecture §10 | open |
   | Obsolete or rejected | the mapping in step 6, with the reason | rejected |

   Keep hardware-independent rules generic; put target-specific names in the hardware profile.
   Never upgrade a proposal into a requirement or decision without the owner's agreement: ask, or
   label it proposed.
4. **Write the destinations.** Cite the source note in each destination's status or provenance line.
5. **Check completeness.** Walk the source section by section and confirm each has a destination
   or a rejection reason. Nothing unique may be lost; the old text stays in git history.
6. **Retire the source.** Replace its body with `Status: historical`, the migration date and a table
   *former section → current home*. If only part is promoted, keep the body, set
   `Status: proposed, partly promoted` and put the same table, for the migrated sections only, under
   the status line.
7. **Update indexes and record it.** Update the notes index in `platform/docs/README.md` and any
   index of the destination repositories. The commit message records the migration; add a
   `platform/governance/decisions.md` line only for a new owner decision that passes its log test.
8. **Verify.** Check that all relative links and anchors resolve. Use the same branch name in every
   repository you changed (`muon branch`), announce them, and run `muon verify` (skill `muon-verify`).
   Mark contract changes additive or breaking in the commit message.
