# Iterations

System-level plans ([engineering process §4](../governance/engineering_process.md#4-changes)). An
iteration plans one domain through the playbook (skill `muon-domain-iteration`) and orders its work
across repositories. It holds no behaviour specs: those, and their changes, live in each component
repository's `openspec/`, and an iteration task links the change that carries it out.

## Layout

```text
iterations/
  <yyyy-mm>-<domain>-iteration-<n>/   copy of _template/
    proposal.md      status, capabilities and their playbook steps, why, scope, decision requests,
                     delegation, revisions
    tasks.md         task table (repository, task, requirement IDs, OpenSpec change, verification, status)
                     and `## Next` (pending actions, questions, hardware validation limits)
    as-is.md         legacy archaeology (step 1, skill `muon-legacy-archaeology`), when there is legacy
    golden-data.md   golden-data plan (step 2), when there is legacy
  archive/           completed iterations, and change records from before 2026-10-26
```

## Status

`proposal.md` starts with `Status:` (`active`, `paused` or `completed`, as in
[`work/index.yml`](../work/index.yml)); its `## Capabilities` table holds each capability's playbook
step (0–8). Decisions are classed and recorded as in skill `muon-domain-iteration`. Register an iteration in the
work index when its proposal and tasks exist. Move it to `archive/` when it is completed.

Records in `archive/` dated before 2026-10-26 are change proposals from the earlier process, which
used this directory (then `changes/`) for spec deltas as well; they are historical.
