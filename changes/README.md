# Change Proposals

Spec-driven changes to the platform ([ADR-010 §3](../docs/adr/ADR-010_spec_driven_domain_iteration.md)).

A change proposal describes **deltas against the living specs**. Specs are
project `SPEC.md` files, `contracts/`, and the platform docs. A proposal is
approved by a human before contracts are frozen and implementation starts.

## Layout

```text
changes/
  <yyyy-mm>-<slug>/      active proposal (copy of _template/)
    proposal.md          why, scope, affected projects, decisions needed
    specs.md             spec deltas (ADDED / MODIFIED / REMOVED requirements)
    contracts.md         contract diff or links to contracts/ commits
    tasks.md             ordered tasks with verification per task
  archive/               merged proposals (deltas already folded into the specs)
```

## Lifecycle

`draft` → `approved` → `contracts-frozen` → `implementing` → `verified` → `archived`

The current status is the `Status:` line at the top of `proposal.md`.
