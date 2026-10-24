# Online Event Builder

Status: historical. The content of this design note was migrated on 2026-10-24; the former text is in
git history. Event building belongs to the future `recon` module of core; its requirements are staged
under `core/daq/doc/` until that module exists.

| Former section | Current home |
|---|---|
| Purpose, placement, online pipeline, boundary rule | [System architecture §5](../architecture/system_architecture.md#5-scientific-processing-and-data); [event builder requirements](../../../core/daq/doc/specs/event-builder.md#ownership-and-boundary) |
| Input from preprocess, output from recon (field lists) | [Pipeline record contracts](../../../core/contracts/science/pipeline/README.md) (proposed) |
| Event identity | [FX3 profile](../../../core/daq/doc/specs/event-builder-fx3.md#event-identity) |
| Completion policy, duplicate handling | [Event builder requirements](../../../core/daq/doc/specs/event-builder.md#completion-and-incomplete-events) (duplicate rule is a proposed default) |
| `event_status`, failure handling | [Event status and reasons](../../../core/daq/doc/specs/event-builder.md#event-status-and-reasons), [failure surfacing](../../../core/daq/doc/specs/event-builder.md#failure-surfacing) |
| Intermediate observability, publication interface | [Observability](../../../core/daq/doc/specs/event-builder.md#observability), [publication](../../../core/daq/doc/specs/event-builder.md#publication) |
| Timestamp requirements | [Host-side aggregation timestamps](../../../core/daq/doc/specs/event-builder.md#host-side-aggregation-timestamps) |
| Event assembly model, minimal component split | [Reference design (non-normative)](../../../core/daq/doc/specs/event-builder.md#reference-design-non-normative) |
| FX3 names (`adm_index`, sync IDs, ADM masks) | [FX3 record mapping](../../../core/daq/doc/specs/event-builder-fx3.md#record-mapping) |
