---
name: muon-new-change
description: Use when the user wants a decision recorded, or a prototype promoted into the spec baseline, as a change proposal in platform/changes/ (ADR-010 §3). Optional while prototyping (ADR-012 §6).
---

# New change proposal

1. Pick a slug and create `platform/changes/<yyyy-mm>-<slug>/` by copying `platform/changes/_template/`.
2. Run `muon list` and list the affected repositories in `proposal.md`.
3. Fill in `proposal.md`: why, scope, out of scope, and **decisions needed (human)**. Do not make those decisions yourself.
4. Write `specs.md` as deltas (ADDED / MODIFIED / REMOVED) against the current `SPEC.md` files and platform docs. Give each requirement an ID (`<AREA>-<NNN>`, ADR-010 §7) and a machine-checkable acceptance criterion.
5. Write `contracts.md` if any `contracts/` file changes. Mark each change as breaking or additive.
6. Write `tasks.md`: ordered tasks, one project per task, with spec IDs and a verification command. Contract tasks come first.
7. Leave `Status: draft` and ask the user to review. Do not implement until the status is `approved`.
