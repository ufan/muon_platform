# Centralized CLI Command Model

## Purpose

This document defines the command model and naming conventions for the centralized detector CLI.

It is intended as an implementation reference for a single top-level tool, tentatively named:

```text
muonctl
```

The CLI is a thin control and observability adapter over subsystem and instrument service APIs. It must not become a second implementation of subsystem logic.

## Design goals

The CLI should be:

- centralized
- subsystem-oriented
- script-friendly
- stable enough for automation
- readable enough for operators
- consistent across all subsystem groups

The CLI must support:

- primitive commands for subsystem-local operations
- coordinated commands at the instrument level
- human-readable output
- machine-readable output
- watch and subscribe workflows

## Top-level command hierarchy

Recommended top-level groups:

```text
muonctl instrument ...
muonctl daq ...
muonctl sensors ...
muonctl gas ...
muonctl thermal ...
muonctl power ...
muonctl bus ...
muonctl telemetry ...
muonctl config ...
muonctl admin ...
```

Meaning:

- `instrument`: high-level coordinated control and readiness actions
- `daq`: DAQ subsystem control and status
- `sensors`: sensor network state, readings, and watches
- `gas`: gas-control actions and status
- `thermal`: cooling and dehumidifier control and status
- `power`: high-voltage and low-voltage control and status
- `bus`: RS485 or Modbus bus diagnostics and device discovery
- `telemetry`: cross-subsystem telemetry queries and live subscriptions
- `config`: configuration inspection and validation
- `admin`: maintenance, diagnostics, and service-level operations

Do not create one independent binary per subsystem unless forced by deployment constraints. Prefer one CLI with coherent naming.

## Command grammar

Recommended general shape:

```text
muonctl <group> <resource-or-subgroup> <verb> [flags]
```

Examples:

```text
muonctl daq state get
muonctl daq run start --profile cosmic
muonctl sensors humidity get --sensor h1
muonctl gas flow set --channel mfc1 --sccm 50
muonctl power hv ramp --channel det0 --target-v 1200
muonctl instrument readiness get
muonctl instrument run start --profile default
```

For simple groups, `<resource-or-subgroup>` may be omitted:

```text
muonctl daq check
muonctl daq stop
muonctl instrument ready
```

## Naming conventions

### Binary name

Use a short, stable binary name:

```text
muonctl
```

Avoid names tied to one subsystem such as `daqctl`, because the CLI is instrument-wide.

### Group names

Use short lowercase plural nouns for subsystem collections:

- `sensors`
- `gas`
- `thermal`
- `power`

Use singular nouns only when the group represents a whole-system role:

- `instrument`
- `telemetry`
- `config`
- `admin`

### Verb names

Use short lowercase verbs.

Preferred verbs:

- `get`
- `list`
- `watch`
- `start`
- `stop`
- `set`
- `enable`
- `disable`
- `open`
- `close`
- `ramp`
- `check`
- `discover`
- `reset`
- `validate`
- `ack`

Avoid synonyms for the same action. Choose one and keep it everywhere.

Preferred pairs:

- use `get`, not `show`
- use `list`, not `ls`
- use `watch`, not `tail`
- use `set`, not `update`
- use `start` and `stop`, not `run` and `halt`
- use `enable` and `disable`, not `on` and `off`

### Flag names

Use long kebab-case flags:

- `--run-id`
- `--device-id`
- `--bus-id`
- `--channel`
- `--target-v`
- `--timeout-ms`

Short flags should be limited to very common cross-cutting options:

- `-h` for help
- `-q` for quiet
- `-v` for verbose

Do not create subsystem-specific one-letter flags unless they are already extremely conventional.

### Resource identifiers

Identifiers passed as flag values should be stable and explicit.

Examples:

- `--sensor temp-01`
- `--channel hv-det-0`
- `--bus-id rs485-a`
- `--device-id plc-main`

Avoid positional arguments for device identity when ambiguity is possible.

## Output conventions

Every command should support predictable output modes.

### Human-readable default

Default output should be concise and readable by operators.

Example:

```text
state: ready
connected_boards: 0x07
run_active: false
health: ok
```

### JSON mode

Every non-trivial command should support:

```text
--json
```

JSON output should be:

- stable
- machine-readable
- single-object or single-array on stdout
- free of extra prose

### Watch mode

Live commands should support either:

- a `watch` verb
- or a `--watch` flag when the base command is naturally readable

Prefer `watch` as a verb for streams and subscriptions.

Examples:

```text
muonctl daq events watch
muonctl sensors temperature watch --sensor temp-01
muonctl telemetry stream watch --topic alarms
```

## Exit code conventions

Use simple, stable process exit semantics:

- `0`: success
- `1`: command or service error
- `2`: invalid user input
- `3`: command accepted but target state or readiness condition not satisfied
- `4`: transport or connectivity failure
- `5`: timeout

This makes CLI composition practical in shell scripts.

## Common global flags

Recommended global flags:

- `--endpoint <url>`
- `--json`
- `--timeout-ms <n>`
- `--watch`
- `--quiet`
- `--verbose`
- `--profile <name>`

If authentication is required later, add:

- `--token`
- `--user`
- `--role`

## Core command categories

Each subsystem group should expose a consistent set of command categories where applicable.

### 1. State and health

Recommended pattern:

```text
muonctl <group> state get
muonctl <group> health get
```

Examples:

```text
muonctl daq state get
muonctl gas health get
muonctl power state get
```

### 2. Discovery and inventory

Recommended pattern:

```text
muonctl <group> list
muonctl <group> discover
```

Use:

- `list` for known configured resources
- `discover` for active probing

Examples:

```text
muonctl sensors list
muonctl bus discover --bus-id rs485-a
muonctl daq check
```

### 3. Get and set operations

Recommended pattern:

```text
muonctl <group> <resource> get
muonctl <group> <resource> set ...
```

Examples:

```text
muonctl gas flow get --channel mfc1
muonctl gas flow set --channel mfc1 --sccm 50
muonctl thermal dehumidifier set --enable true
```

### 4. Start and stop operations

Recommended pattern:

```text
muonctl <group> start
muonctl <group> stop
```

Or for named operations:

```text
muonctl <group> run start
muonctl <group> run stop
```

Examples:

```text
muonctl daq start
muonctl daq stop
muonctl instrument run start --profile standard
muonctl instrument safe-shutdown start
```

### 5. Watch and subscribe operations

Recommended pattern:

```text
muonctl <group> <resource> watch
muonctl telemetry stream watch --topic <topic>
```

Examples:

```text
muonctl daq metrics watch
muonctl sensors humidity watch --sensor h1
muonctl telemetry stream watch --topic alarms
```

## Group-specific command model

### `instrument`

This group exposes coordinated high-level actions. It should call orchestrator APIs.

Recommended commands:

```text
muonctl instrument state get
muonctl instrument health get
muonctl instrument readiness get
muonctl instrument ready
muonctl instrument run start --profile <name>
muonctl instrument run stop
muonctl instrument safe-shutdown start
muonctl instrument alarms list
muonctl instrument alarms watch
```

Naming rule:

- use imperative verbs only for orchestrator-backed composite actions
- do not implement orchestration locally in the CLI

### `daq`

This group exposes DAQ subsystem primitives.

Recommended commands:

```text
muonctl daq state get
muonctl daq health get
muonctl daq check
muonctl daq configure --profile <name>
muonctl daq start
muonctl daq stop
muonctl daq reset
muonctl daq metrics watch
muonctl daq raw watch
muonctl daq decoded watch
muonctl daq runs list
muonctl daq run current get
```

Naming rule:

- reserve `raw watch` and `decoded watch` for observability streams
- use `configure` for profile or parameter application

### `sensors`

This group exposes sensor inventory and reading access.

Recommended commands:

```text
muonctl sensors list
muonctl sensors state get
muonctl sensors health get
muonctl sensors reading get --sensor <id>
muonctl sensors reading watch --sensor <id>
muonctl sensors alarms list
muonctl sensors alarms watch
```

Optional aliases by class may exist, but the canonical model should remain stable:

```text
muonctl sensors temperature get --sensor temp-01
muonctl sensors humidity watch --sensor hum-01
```

### `gas`

Recommended commands:

```text
muonctl gas state get
muonctl gas health get
muonctl gas flow get --channel <id>
muonctl gas flow set --channel <id> --sccm <n>
muonctl gas valve open --valve <id>
muonctl gas valve close --valve <id>
muonctl gas pressure get --gauge <id>
muonctl gas purge start --profile <name>
muonctl gas purge stop
muonctl gas alarms watch
```

### `thermal`

Recommended commands:

```text
muonctl thermal state get
muonctl thermal health get
muonctl thermal temperature get
muonctl thermal dehumidifier enable
muonctl thermal dehumidifier disable
muonctl thermal cooling enable
muonctl thermal cooling disable
muonctl thermal metrics watch
```

### `power`

Recommended commands:

```text
muonctl power state get
muonctl power health get
muonctl power hv get --channel <id>
muonctl power hv set --channel <id> --target-v <n>
muonctl power hv ramp --channel <id> --target-v <n>
muonctl power hv enable --channel <id>
muonctl power hv disable --channel <id>
muonctl power lv enable --channel <id>
muonctl power lv disable --channel <id>
muonctl power trips list
muonctl power trips watch
```

### `bus`

This group exposes bus diagnostics and device-level discovery. It is primarily for bring-up and debugging.

Recommended commands:

```text
muonctl bus list
muonctl bus state get --bus-id <id>
muonctl bus discover --bus-id <id>
muonctl bus scan --bus-id <id>
muonctl bus stats get --bus-id <id>
muonctl bus errors watch --bus-id <id>
```

### `telemetry`

This group provides cross-subsystem telemetry access.

Recommended commands:

```text
muonctl telemetry latest get --topic <topic>
muonctl telemetry query --topic <topic> --since <ts> --until <ts>
muonctl telemetry stream watch --topic <topic>
```

## Composite versus primitive commands

Primitive commands should always exist below any composite orchestration command.

Examples:

- primitive:
  `muonctl gas flow set --channel mfc1 --sccm 50`
- primitive:
  `muonctl power hv ramp --channel det0 --target-v 1200`
- composite:
  `muonctl instrument ready`

Rule:

- primitives are for direct subsystem actions
- composites are for orchestrator-backed workflows

Do not hide primitive operations behind only composite workflows.

## Watch command behavior

Watch commands should:

- continue until interrupted
- write updates to stdout
- write diagnostics to stderr
- support `--json`
- reconnect by policy when used against remote APIs

When using human-readable output, each update should be one logical record block.
When using `--json`, prefer newline-delimited JSON objects.

## Error message conventions

Human-readable errors should be short and actionable.

Example:

```text
error: instrument not ready
reason: humidity above threshold
hint: run `muonctl instrument readiness get --json`
```

JSON errors should include:

- `error`
- `reason`
- `code`
- `retryable`

## Backward compatibility rule

Once a command path is published for operator or automation use, avoid breaking it casually.

Allowed evolution:

- add new flags
- add new output fields in JSON where safe
- add new subcommands

Avoid:

- renaming stable verbs
- changing field meanings silently
- moving commands across groups without compatibility aliases

## API mapping rule

CLI commands should map cleanly to service APIs.

Recommended mapping:

- request/response commands -> HTTP endpoints
- watch commands -> WebSocket or SSE subscriptions

This keeps the CLI implementation thin and consistent with web clients.

## Recommended first implementation scope

Start with a minimal but consistent subset:

```text
muonctl instrument state get
muonctl instrument readiness get
muonctl daq state get
muonctl daq check
muonctl daq start
muonctl daq stop
muonctl sensors list
muonctl gas state get
muonctl power state get
muonctl telemetry stream watch --topic alarms
```

Then expand group-by-group without changing the naming model.
