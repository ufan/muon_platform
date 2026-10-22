# Contract changes

| Contract | Path in `contracts/` | Change | Compatibility |
|---|---|---|---|
| Device state machine | `fsm/daq_device.yaml` | new, from `daq/doc/specs/state_machine.md` + `daq/ref/fx3/gen1` state model | additive (0.x) |
| Service API | `api/daq.*` | new, from `daq/doc/specs/service-api.md` | additive (0.x) |
| Raw capture + run metadata | `persistence/raw_capture.*` | new | additive (0.x) |
| Raw stream to consumers | `pipeline/raw_stream.*` | new | additive (0.x) |
| Wire protocol | `wire/` | **removed**: owned by `daq/ref/fx3/gen1/` (decision 1, 2026-10-22) | n/a |
