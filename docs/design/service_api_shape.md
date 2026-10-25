# Service API Shape

Status: proposed. Scope: the **external** operator/web-facing API of the instrument (HTTP/JSON, WebSocket) and its mapping to the operator CLI. Internal domain-service contracts remain protobuf/gRPC ([system architecture §3](../architecture/system_architecture.md#3-control-and-services)); an HTTP surface would be an adapter over them. `muonctl` is the planned instrument operator CLI, not the workspace `muon` tool. Per [ADR-014](../adr/ADR-014_slow_control_domains_and_transports.md), the `thermal` (cooling/dehumidifier) commands are out of scope, and `bus` diagnostics address configured host ports, not a fixed set of buses.

## Purpose

This document defines the service API shape for the detector instrument so that:

- the centralized CLI can map cleanly to concrete endpoints
- web UIs can reuse the same contracts
- subsystem services and the instrument orchestrator expose consistent interfaces

This is an interface-shape reference, not a full OpenAPI document.

## Design goals

The API should be:

- resource-oriented
- stable enough for automation
- consistent across subsystem groups
- suitable for both local and remote clients
- split cleanly between request/response control and live subscriptions

The API should support:

- primitive subsystem commands
- instrument-level orchestration commands
- state and health queries
- telemetry queries
- real-time event and metrics streams

## Transport split

Use two main API styles:

- HTTP/JSON for request/response commands and queries
- WebSocket for live streams and watch/subscription workflows

Optional:

- SSE for lightweight status or alarm subscriptions when a full WebSocket client is unnecessary

Recommended base path:

```text
/api/v1
```

Recommended WebSocket base:

```text
/ws/v1
```

## Top-level API groups

The API should mirror the CLI command groups.

Recommended namespaces:

- `/api/v1/instrument/*`
- `/api/v1/daq/*`
- `/api/v1/sensors/*`
- `/api/v1/gas/*`
- `/api/v1/thermal/*`
- `/api/v1/power/*`
- `/api/v1/bus/*`
- `/api/v1/telemetry/*`
- `/api/v1/config/*`
- `/api/v1/admin/*`

This lets `muonctl` map to predictable URLs.

## API design rules

### 1. Queries use `GET`

Use `GET` for:

- state
- health
- inventory
- current readings
- historical query requests that fit query parameters

Examples:

- `GET /api/v1/daq/state`
- `GET /api/v1/gas/health`
- `GET /api/v1/sensors`

### 2. Commands use `POST`

Use `POST` for state-changing or procedural operations.

Examples:

- `POST /api/v1/daq/check`
- `POST /api/v1/daq/start`
- `POST /api/v1/power/hv/ramp`
- `POST /api/v1/instrument/run/start`

Do not overload `GET` with imperative actions.

### 3. Resource updates use `POST` or `PATCH` by policy

To keep the first version simple, it is acceptable to use `POST` command endpoints for set-like operations.

Examples:

- `POST /api/v1/gas/flow/set`
- `POST /api/v1/thermal/dehumidifier/enable`

If later you want stricter REST semantics, you may adopt `PATCH` for resource-property changes, but the command-oriented form is simpler for operational systems.

### 4. Watch flows use WebSocket topics

Any CLI `watch` command should map to a WebSocket subscription topic, not to repeated polling.

Examples:

- `muonctl daq metrics watch`
- `muonctl telemetry stream watch --topic alarms`

## Common response envelope

Recommended HTTP response envelope:

```json
{
  "ok": true,
  "data": {},
  "error": null,
  "meta": {
    "request_id": "req_123",
    "ts": "2026-04-08T12:00:00Z"
  }
}
```

On error:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "instrument_not_ready",
    "reason": "humidity above threshold",
    "retryable": false
  },
  "meta": {
    "request_id": "req_124",
    "ts": "2026-04-08T12:00:01Z"
  }
}
```

Rules:

- `ok` is always present
- `data` is null only on failure
- `error` is null only on success
- `meta` always exists

## Common object categories

The API should return stable shapes for these categories:

- state object
- health object
- command result
- telemetry sample
- alarm event
- interlock event
- inventory item
- run summary

## Common fields

### State object

Recommended fields:

```json
{
  "state": "ready",
  "health": "ok",
  "degraded": false,
  "updated_at": "2026-04-08T12:00:00Z"
}
```

### Health object

Recommended fields:

```json
{
  "health": "ok",
  "degraded": false,
  "active_alarms": 0,
  "active_interlocks": 0,
  "updated_at": "2026-04-08T12:00:00Z"
}
```

### Command result

Recommended fields:

```json
{
  "accepted": true,
  "completed": true,
  "result": "ok",
  "target_state": "acquiring",
  "message": "DAQ start accepted"
}
```

### Telemetry sample

Recommended fields:

```json
{
  "topic": "sensors.temperature",
  "source": "temp-01",
  "value": 22.5,
  "unit": "C",
  "quality": "ok",
  "ts": "2026-04-08T12:00:00Z"
}
```

## Instrument API

This namespace is for orchestrator-backed coordinated operations.

### Queries

- `GET /api/v1/instrument/state`
- `GET /api/v1/instrument/health`
- `GET /api/v1/instrument/readiness`
- `GET /api/v1/instrument/alarms`
- `GET /api/v1/instrument/interlocks`

### Commands

- `POST /api/v1/instrument/ready`
- `POST /api/v1/instrument/run/start`
- `POST /api/v1/instrument/run/stop`
- `POST /api/v1/instrument/safe-shutdown/start`
- `POST /api/v1/instrument/alarms/ack`

### Example request

`POST /api/v1/instrument/run/start`

```json
{
  "profile": "standard"
}
```

### Example CLI mapping

```text
muonctl instrument run start --profile standard
-> POST /api/v1/instrument/run/start
```

## DAQ API

This namespace exposes DAQ subsystem primitives.

### Queries

- `GET /api/v1/daq/state`
- `GET /api/v1/daq/health`
- `GET /api/v1/daq/runs`
- `GET /api/v1/daq/runs/current`

### Commands

- `POST /api/v1/daq/connect`
- `POST /api/v1/daq/check`
- `POST /api/v1/daq/configure`
- `POST /api/v1/daq/start`
- `POST /api/v1/daq/stop`
- `POST /api/v1/daq/reset`

### Example request

`POST /api/v1/daq/configure`

```json
{
  "profile": "cosmic",
  "adm_mask": "0x07"
}
```

### Example CLI mapping

```text
muonctl daq check
-> POST /api/v1/daq/check

muonctl daq run current get
-> GET /api/v1/daq/runs/current
```

## Sensors API

### Queries

- `GET /api/v1/sensors`
- `GET /api/v1/sensors/state`
- `GET /api/v1/sensors/health`
- `GET /api/v1/sensors/readings/{sensor_id}`
- `GET /api/v1/sensors/alarms`

### Commands

- `POST /api/v1/sensors/discover`
- `POST /api/v1/sensors/alarms/ack`

### Example CLI mapping

```text
muonctl sensors list
-> GET /api/v1/sensors

muonctl sensors reading get --sensor temp-01
-> GET /api/v1/sensors/readings/temp-01
```

## Gas API

### Queries

- `GET /api/v1/gas/state`
- `GET /api/v1/gas/health`
- `GET /api/v1/gas/flow/{channel_id}`
- `GET /api/v1/gas/pressure/{gauge_id}`
- `GET /api/v1/gas/alarms`

### Commands

- `POST /api/v1/gas/flow/set`
- `POST /api/v1/gas/valves/{valve_id}/open`
- `POST /api/v1/gas/valves/{valve_id}/close`
- `POST /api/v1/gas/purge/start`
- `POST /api/v1/gas/purge/stop`

### Example request

`POST /api/v1/gas/flow/set`

```json
{
  "channel": "mfc1",
  "sccm": 50
}
```

## Thermal API

### Queries

- `GET /api/v1/thermal/state`
- `GET /api/v1/thermal/health`
- `GET /api/v1/thermal/metrics`

### Commands

- `POST /api/v1/thermal/cooling/enable`
- `POST /api/v1/thermal/cooling/disable`
- `POST /api/v1/thermal/dehumidifier/enable`
- `POST /api/v1/thermal/dehumidifier/disable`

## Power API

### Queries

- `GET /api/v1/power/state`
- `GET /api/v1/power/health`
- `GET /api/v1/power/hv/{channel_id}`
- `GET /api/v1/power/lv/{channel_id}`
- `GET /api/v1/power/trips`

### Commands

- `POST /api/v1/power/hv/set`
- `POST /api/v1/power/hv/ramp`
- `POST /api/v1/power/hv/{channel_id}/enable`
- `POST /api/v1/power/hv/{channel_id}/disable`
- `POST /api/v1/power/lv/{channel_id}/enable`
- `POST /api/v1/power/lv/{channel_id}/disable`

### Example request

`POST /api/v1/power/hv/ramp`

```json
{
  "channel": "det0",
  "target_v": 1200
}
```

## Bus API

This namespace is primarily for RS485 or Modbus diagnostics and bring-up.

### Queries

- `GET /api/v1/bus`
- `GET /api/v1/bus/{bus_id}/state`
- `GET /api/v1/bus/{bus_id}/stats`

### Commands

- `POST /api/v1/bus/{bus_id}/discover`
- `POST /api/v1/bus/{bus_id}/scan`
- `POST /api/v1/bus/{bus_id}/reset`

## Telemetry API

This namespace provides cross-subsystem telemetry access.

### Queries

- `GET /api/v1/telemetry/latest?topic=<topic>`
- `GET /api/v1/telemetry/query?topic=<topic>&since=<ts>&until=<ts>`

### Commands

Usually none for first version, unless you need explicit export or replay jobs.

### Example CLI mapping

```text
muonctl telemetry latest get --topic alarms
-> GET /api/v1/telemetry/latest?topic=alarms
```

## Config API

### Queries

- `GET /api/v1/config/profiles`
- `GET /api/v1/config/profiles/{profile_name}`
- `GET /api/v1/config/validate`

### Commands

- `POST /api/v1/config/validate`
- `POST /api/v1/config/reload`

## Admin API

This namespace is for service-level diagnostics and maintenance.

### Queries

- `GET /api/v1/admin/version`
- `GET /api/v1/admin/health`
- `GET /api/v1/admin/services`

### Commands

- `POST /api/v1/admin/reload`
- `POST /api/v1/admin/shutdown`

## WebSocket shape

WebSocket is the preferred transport for CLI `watch` commands and UI live dashboards.

Recommended endpoint:

```text
/ws/v1/stream
```

Recommended initial subscribe message:

```json
{
  "action": "subscribe",
  "topics": [
    "instrument.state",
    "daq.metrics"
  ]
}
```

Recommended unsubscribe message:

```json
{
  "action": "unsubscribe",
  "topics": [
    "daq.metrics"
  ]
}
```

Recommended event envelope:

```json
{
  "topic": "daq.metrics",
  "ts": "2026-04-08T12:00:00Z",
  "data": {
    "byte_rate": 1200000,
    "packet_rate": 340
  }
}
```

## Recommended stream topics

The topic names should be lowercase dot-separated identifiers.

Recommended topic families:

- `instrument.state`
- `instrument.health`
- `instrument.readiness`
- `instrument.alarms`
- `instrument.interlocks`
- `daq.state`
- `daq.metrics`
- `daq.events`
- `daq.raw`
- `daq.decoded`
- `sensors.readings`
- `sensors.alarms`
- `gas.state`
- `gas.metrics`
- `gas.alarms`
- `thermal.state`
- `thermal.metrics`
- `power.state`
- `power.trips`
- `bus.errors`
- `telemetry.<topic>`

## CLI watch mapping

Recommended mapping from CLI to WebSocket topics:

- `muonctl daq metrics watch` -> subscribe `daq.metrics`
- `muonctl daq raw watch` -> subscribe `daq.raw`
- `muonctl daq decoded watch` -> subscribe `daq.decoded`
- `muonctl instrument alarms watch` -> subscribe `instrument.alarms`
- `muonctl telemetry stream watch --topic alarms` -> subscribe `telemetry.alarms`

## Synchronous versus asynchronous command model

For the first version, prefer synchronous completion for most operational commands.

Examples:

- `POST /api/v1/daq/check` returns when the check result is known
- `POST /api/v1/daq/start` returns when the start command has been accepted or failed

For long-running operations, use an operation resource.

Example:

- `POST /api/v1/instrument/safe-shutdown/start`
- response contains `operation_id`
- client may poll `GET /api/v1/admin/operations/{operation_id}`

## Error mapping to CLI exit codes

Recommended mapping:

- HTTP `200` with `ok=true` -> CLI exit `0`
- HTTP `400` -> CLI exit `2`
- HTTP `409` for state conflict or readiness conflict -> CLI exit `3`
- HTTP `502` or `503` for transport or subsystem unavailable -> CLI exit `4`
- HTTP `504` -> CLI exit `5`

CLI should still inspect the JSON `error.code` and `error.reason`.

## Authentication and authorization shape

If the system adds remote control security, keep the API shape stable.

Recommended approach:

- bearer token in `Authorization` header for HTTP
- token on WebSocket handshake or initial auth message

Role separation should distinguish at least:

- observe
- operate
- administer

## Recommended first implementation scope

Implement these first:

- instrument state and readiness endpoints
- DAQ state, check, start, stop endpoints
- sensor list and reading endpoints
- gas state endpoint
- power state endpoint
- shared `/ws/v1/stream` endpoint with a small set of topics:
  - `instrument.alarms`
  - `daq.metrics`
  - `daq.events`

That is enough to back the first useful `muonctl` commands and a basic web UI.
