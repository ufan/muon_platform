# Contract changes

| Contract | Path in `core/contracts/` (repository model) | Change | Compatibility |
|---|---|---|---|
| Device state machine | `science/fsm/daq_device.yaml` | new, from `daq/doc/specs/state_machine.md` + `daq/ref/fx3/gen1` state model | additive (0.x) |
| Domain-service pattern | `system/domain_service/*` | new: lifecycle, health, alarms, capability conventions that the DAQ API builds on (future domains copy it) | additive (0.x) |
| Service API | `science/api/daq.*` | new, from `daq/doc/specs/service-api.md`, on top of `system/domain_service` | additive (0.x) |
| Raw capture + run metadata | `science/persistence/raw_capture.*` | new; reserves provenance and time fields (decision 4) | additive (0.x) |
| Time base | `system/time/*` | new: `Timestamp`, `ClockCorrelation` (system architecture §6) | additive (0.x) |
| Raw stream to consumers | `science/pipeline/raw_stream.*` | new | additive (0.x) |
| Wire protocol | `wire/` | **removed**: owned by `core/daq/ref/fx3/gen1/` (decision 1, 2026-10-22) | n/a |

While core is the only consumer, a contract and its consumer change in one commit in core (engineering process §4).
