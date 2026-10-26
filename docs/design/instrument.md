# Instrument layer design

Status: proposed. Input for the planned `muon_instrument` (coordination, operator CLI and external
API). Not a decision; the binding boundaries are in the [system architecture](../architecture/system_architecture.md),
[ADR-003](../adr/ADR-003_hardware_domain_services.md) and [ADR-014](../adr/ADR-014_slow_control_domains_and_transports.md).
Consolidated 2026-10-25 from the former `instrument_architecture.md`, `service_api_shape.md` and
`cli_command_model.md` (full text in git).

## 1. Why an instrument layer

The detector is a coordinated instrument, not only a DAQ endpoint. Operation needs rules that span
domains, for example:

- do not start acquisition until HV is within range;
- do not enable HV unless gas flow and pressure are valid;
- stop acquisition or ramp down HV if humidity exceeds a threshold;
- continue in degraded mode if a non-critical environment sensor is lost.

These are neither DAQ rules nor device rules. Without an explicit layer they scatter into UI code,
scripts, drivers and DAQ recovery logic.

## 2. Layers

| Layer | Owns | Must not |
|---|---|---|
| Domain controllers and transports | device communication, polling, retries, timeouts, per-port bus ownership (ADR-014) | make instrument policy |
| Domain services (DAQ, HV, LV, gas, pose, environment) | domain state machine, configuration, normalized telemetry and alarms, sequencing inside the domain | coordinate other domains |
| Instrument orchestrator | operating modes, readiness, interlock policy, cross-domain sequencing | talk to transports |
| Operator and automation adapters (CLI, web UI, scripts) | presentation and composition of service calls | contain device or orchestration logic |

The CLI and web UI are clients of the same instrument and domain APIs.

## 3. Instrument states

Separate from the DAQ state machine:

| State | Meaning |
|---|---|
| `offline` | core services unavailable |
| `initializing` | discovery and baseline checks |
| `standby` | powered, not ready for detector operation |
| `conditioning` | establishing gas, environment and voltage conditions |
| `ready` | all preconditions for acquisition satisfied |
| `running` | detector operating, usually acquiring |
| `degraded` | operating with reduced capability under explicit policy |
| `interlocked` | a safety or critical condition blocks operation |
| `safe_shutdown` | controlled shutdown in progress |
| `maintenance` | operator service mode; some automation bypassed under policy |

## 4. Policies

- **Readiness** (`→ ready`): DAQ link ready; gas flow and pressure in range; humidity below
  threshold; LV healthy; HV available within standby policy.
- **Run start** (`→ running`): DAQ ready, gas stable, power operational, no active interlock.
- **Interlocks:** triggers such as high humidity, over-temperature, gas pressure fault, HV trip or
  PLC emergency; actions such as rejecting run start, stopping DAQ, ramping down HV, closing valves,
  notifying operators, entering `interlocked` or `safe_shutdown`. Categories: block-start, degrade,
  emergency-stop. Protection that must not depend on the host stays in the domain controller or
  device (ADR-014).

## 5. Operator CLI (`muonctl`)

One instrument-wide CLI (not the workspace `muon` tool), grouped by domain:
`muonctl <group> [<resource>] <verb> [flags]`, groups `instrument`, `daq`, `hv`, `lv`, `gas`,
`pose`, `environment`, `telemetry`, `config`, `admin`.

- **Primitive and composite:** every domain action has a primitive command
  (`muonctl gas flow set --channel mfc1 --sccm 50`); composites (`muonctl instrument ready`) call
  the orchestrator and never reimplement it.
- **Vocabulary:** one verb per action (`get`, `list`, `watch`, `set`, `start`/`stop`,
  `enable`/`disable`, `ramp`, `check`, `ack`); long kebab-case flags; explicit identifiers
  (`--channel hv-det-0`) rather than positional ones.
- **Output:** concise human output by default; `--json` gives one stable object on stdout;
  `watch` streams one record per update (newline-delimited JSON with `--json`), diagnostics on stderr.
- **Errors and exit codes:** errors carry `code`, `reason`, `retryable` and a hint. Exit 0 success,
  2 invalid request, 3 state or readiness conflict, 4 subsystem unavailable, 5 timeout.
- **Compatibility:** published commands only gain flags, fields or subcommands; renames need aliases.
- **First scope:** instrument state and readiness; DAQ state, check, start, stop; environment list;
  gas and power state; alarm watch.

## 6. External API

Internal services use protobuf/gRPC (ADR-003). If remote web clients need HTTP, an API gateway
adapts the same services:

- request/response as HTTP/JSON under `/api/v1/<group>/…` with an envelope
  `{ok, data, error{code, reason, retryable}, meta{request_id, ts}}`;
- live data on one WebSocket (`/ws/v1/stream`) with subscribe/unsubscribe messages and events
  `{topic, ts, data}`; topics are lowercase and dotted (`instrument.alarms`, `daq.metrics`, `gas.state`);
- long operations return an operation ID to poll;
- remote access uses bearer tokens with roles observe, operate and administer.

Shared object shapes: state, health, command result, telemetry sample, alarm, interlock event,
inventory item, run summary.

## 7. Data the instrument persists

Besides DAQ raw data: environment telemetry, gas and power history, the alarm and interlock log,
and run-to-condition correlation metadata (feeding conditions, system architecture §6).

## 8. Next design steps

1. instrument state machine and transitions;
2. normalized health and alarm schemas (with `core/contracts/system/`);
3. interlock policy categories per domain;
4. how run metadata joins telemetry.
