# Instrument-Level System Architecture

Status: proposed (design input for the planned `muon_instrument` coordinator; not a decision). Repository ownership follows the [repository model](../architecture/repository_model.md); the ownership section below is historical. The bus description is an unconfirmed observation of current hardware, not the approved topology; see [system architecture §10](../architecture/system_architecture.md#10-open-points-and-document-discrepancies).

## Purpose

This note widens the system design from DAQ-only control to full detector-instrument control.

The detector system is not only a data-acquisition endpoint. It is a coordinated instrument made of multiple physical subsystems that may need to cooperate to maintain detector performance, stability, and safety.

The system design should therefore distinguish:

- subsystem services
- instrument-level orchestration
- online data pipeline
- centralized operator and automation tool surfaces

## Subsystem inventory

The current detector instrument includes at least:

1. data acquisition
2. sensor network
3. gas control
4. cooling and dehumidifier
5. voltage supply

### 1. Data acquisition

Responsibilities:

- detector readout control
- run/session lifecycle
- raw stream ingest
- immediate persistence
- live fan-out into the online pipeline

Primary protocol:

- custom wire protocol over USB/FX3 or equivalent transport

### 2. Sensor network

Examples:

- humidity
- temperature
- vibration
- inclinometer

Responsibilities:

- sensor polling
- timestamped telemetry acquisition
- health thresholds
- alarm generation

Primary protocol:

- typically Modbus over RS485

### 3. Gas control

Examples:

- mass flow controller
- solenoid valve
- pressure gauge
- PLC integration

Responsibilities:

- gas path actuation
- flow and pressure regulation
- interlock conditions
- purge / open / close sequences

Primary protocol:

- typically Modbus over RS485

### 4. Cooling and dehumidifier

Responsibilities:

- ambient or cabinet thermal control
- humidity control
- fault reporting
- operational enable/disable

Primary protocol:

- typically Modbus over RS485 or vendor-specific control

### 5. Voltage supply

Responsibilities:

- high-voltage supply for detector operation
- low-voltage supply for supporting electronics
- ramp-up and ramp-down control
- trip detection
- interlock response

Primary protocol:

- Modbus or vendor-specific control, depending on the supply modules

## Bus topology implication

When this note was written, most non-DAQ subsystems used Modbus and were grouped into three RS485 buses. This is an unconfirmed description of current hardware; the [management bus specification](../requirements/instrument_management_bus_requirement.md) proposes a single RS-485 bus with COBS/protobuf, and engineering context names CAN-FD as a later evolution. The approved topology is open ([system architecture §10](../architecture/system_architecture.md#10-open-points-and-document-discrepancies)).

That means the architecture should not model every device as an unrelated standalone service. It should explicitly represent:

- bus-level communication ownership
- device addressing on each bus
- polling and command serialization per bus
- fault isolation per bus

Recommended layering:

```text
instrument service layer
-> subsystem service
-> bus manager
-> protocol adapter
-> physical bus or transport
```

For RS485/Modbus paths, one process or module should own arbitration on each bus.

## Required abstraction layers

The system should be designed as at least three layers.

### Layer 1: Device and bus adapters

This layer owns direct communication with hardware.

Examples:

- DAQ transport adapter
- RS485 bus manager
- Modbus client adapter
- HV supply vendor driver

Responsibilities:

- connect/disconnect
- command serialization
- polling
- retries and timeouts
- low-level protocol validation

This layer should not make instrument-level policy decisions.

### Layer 2: Subsystem services

This layer owns the runtime behavior of one subsystem family.

Recommended subsystem services:

- `daq_service`
- `sensor_service`
- `gas_service`
- `thermal_service`
- `power_service`

Responsibilities:

- subsystem state machine
- subsystem configuration
- normalized telemetry and alarms
- device-specific sequencing inside the subsystem
- web-visible status and control API

Each subsystem service should expose:

- state
- health
- commands
- telemetry/events

### Layer 3: Instrument orchestrator

This is the missing higher abstraction you are calling out.

The instrument orchestrator should sit above the subsystem services and own:

- cross-subsystem coordination
- run readiness policy
- detector operating modes
- interlock evaluation
- automatic sequencing
- high-level states such as standby, conditioning, ready, running, safe-shutdown

This layer should not talk directly to hardware transports except through subsystem services.

### Layer 4: Operator and automation adapters

This layer exposes the system to users and scripts.

Recommended adapters:

- centralized CLI toolset
- local web UI
- remote web UI
- automation clients

This layer should remain thin. It should compose subsystem and instrument commands through service APIs rather than owning device logic.

## Why the instrument layer is necessary

Real operation will often require rules such as:

- do not start DAQ acquisition until HV is within range
- do not enable HV unless gas flow and pressure are valid
- stop acquisition or ramp down HV if humidity exceeds threshold
- hold detector in standby if cooling or dehumidification is unhealthy
- switch to degraded operation if a non-critical environmental sensor is lost

Those are not DAQ rules and not pure Modbus rules. They are instrument-level coordination rules.

Without an explicit instrument layer, these policies get scattered into:

- UI code
- scripts
- device drivers
- DAQ recovery logic

That would make the system fragile and hard to certify operationally.

## Recommended top-level system model

```text
                         +---------------------------+
                         | centralized CLI toolset   |
                         +-------------+-------------+
                                       |
                         +---------------------------+
                         | local / remote web UI     |
                         +-------------+-------------+
                                       |
                         +-------------v-------------+
                         | instrument API gateway    |
                         | HTTP + WebSocket          |
                         +-------------+-------------+
                                       |
                         +-------------v-------------+
                         | instrument orchestrator   |
                         | modes, readiness, safety  |
                         +------+------+------+------+
                                |      |      | 
               +----------------+      |      +----------------+
               |                       |                       |
      +--------v--------+    +---------v--------+    +---------v--------+
      | daq_service     |    | gas_service      |    | power_service    |
      +--------+--------+    +---------+--------+    +---------+--------+
               |                       |                       |
      +--------v--------+    +---------v--------+    +---------v--------+
      | daq transport   |    | rs485/modbus bus |    | rs485/modbus bus |
      +-----------------+    +------------------+    +------------------+

      +-----------------+    +------------------+
      | sensor_service  |    | thermal_service  |
      +--------+--------+    +---------+--------+
               |                       |
      +--------v-----------------------v--------+
      | rs485/modbus buses and adapters         |
      +-----------------------------------------+
```

The CLI and the web UI should both be first-class clients of the same instrument and subsystem APIs.

## Instrument operating states

The instrument orchestrator should have its own state machine, separate from the DAQ state machine.

Recommended high-level instrument states:

- `offline`
- `initializing`
- `standby`
- `conditioning`
- `ready`
- `running`
- `degraded`
- `interlocked`
- `safe_shutdown`
- `maintenance`

Meaning:

- `offline`: core services not available
- `initializing`: subsystem discovery and baseline checks in progress
- `standby`: powered but not ready to operate detector
- `conditioning`: environment, gas, thermal, and voltage conditions being established
- `ready`: all preconditions satisfied for acquisition
- `running`: detector operation active, usually including DAQ acquisition
- `degraded`: operation allowed with reduced capability under explicit policy
- `interlocked`: a safety or critical condition blocks normal operation
- `safe_shutdown`: controlled shutdown sequence in progress
- `maintenance`: operator-driven service mode with some interlocks or automations intentionally bypassed under policy

## Coordination examples

### Readiness policy

The instrument should only transition to `ready` when all required subsystem predicates are true.

Examples:

- DAQ link ready
- gas flow within expected range
- gas pressure within expected range
- humidity below threshold
- thermal subsystem healthy
- low voltage healthy
- high voltage available and within allowed standby policy

### Start-run policy

Before transitioning to `running`, the orchestrator may require:

- DAQ subsystem in `ready`
- gas subsystem in `stable_flow`
- power subsystem in `operational`
- no active interlock

### Interlock policy

Example triggers:

- high humidity
- over-temperature
- gas pressure fault
- HV trip
- PLC emergency state

Possible actions:

- reject run start
- stop DAQ
- ramp down HV
- close solenoid valve
- notify operators
- enter `interlocked` or `safe_shutdown`

## Service ownership recommendation

> Historical. Current ownership: [repository model](../architecture/repository_model.md). DAQ is a module of `core`; the instrument orchestrator belongs to the planned `muon_instrument`; shared system schemas are staged in `core/contracts/system/` before extraction to `muon_contracts`; detector/site payloads go to the planned conditions payload repository; operational configuration belongs to the instrument. The list below is kept for rationale.

Do not fold all of this into `daq/`.

Recommended ownership:

- `daq/`: DAQ subsystem service and raw data path
- future `control/` or `instrument/`: instrument orchestrator and non-DAQ subsystem services
- `protocol/`: shared schemas for telemetry, commands, status, alarms, and events
- `config/`: site- and detector-specific configuration for buses, device addresses, thresholds, and policies

If you keep everything in one repository for now, the top-level domain boundaries should still be preserved conceptually.

## Centralized CLI requirement

A centralized CLI toolset is compatible with this architecture and should be preferred as a first-class control surface.

Reasons:

- flexible manual operations
- script-friendly automation
- easy composition of larger coordinated procedures
- usable in local, remote, and headless environments
- lower operational dependency than a GUI

### CLI design rule

The CLI should be centralized at the instrument level, but organized by subsystem subcommand groups.

Recommended shape:

```text
muonctl instrument ...
muonctl daq ...
muonctl sensors ...
muonctl gas ...
muonctl thermal ...
muonctl power ...
muonctl bus ...
muonctl telemetry ...
```

The `instrument` group should expose higher-level coordinated actions.

The subsystem groups should expose primitive commands suitable for scripting and composition.

### Primitive-command principle

Primitive commands are especially important because they can be combined into larger procedures by:

- shell scripts
- task runners
- orchestration services
- test harnesses
- operators during bring-up and debugging

Examples:

```text
muonctl gas status
muonctl gas set-flow --channel 1 --sccm 50
muonctl power hv ramp --channel det0 --target 1200
muonctl sensors watch temperature
muonctl daq check
muonctl daq configure --profile cosmic
muonctl daq start
muonctl instrument ready
muonctl instrument run start --profile standard
```

### CLI implementation rule

The CLI should not bypass subsystem services and talk directly to hardware by default.

It should call the same stable interfaces used by the web UI and automation systems:

- HTTP API for request/response commands
- WebSocket or SSE for watch and subscribe commands

This keeps behavior consistent across:

- CLI
- UI
- automated orchestration

### CLI output modes

To make the CLI useful both for humans and automation, prefer explicit output modes:

- human-readable default output
- `--json` for machine-readable output
- watch mode for live telemetry and state updates

Examples:

```text
muonctl daq state --json
muonctl sensors get humidity --json
muonctl gas watch pressure
muonctl instrument events watch
```

### CLI coordination role

The CLI is a good place for operator-visible composite actions, but only at the adapter layer.

Examples:

- `muonctl instrument ready`
- `muonctl instrument safe-shutdown`
- `muonctl instrument run start`

Those composite actions should invoke orchestrator APIs, not reimplement orchestration logic locally in the CLI.

### Repository impact

The current design should therefore include a centralized CLI adapter in addition to web UI adapters.

Recommended ownership:

- instrument-level CLI in future `control/` or `instrument/`
- DAQ-specific adapter group under `daq/` for subsystem-local development if needed
- shared command/result schemas in `protocol/`

If the repository stays unified for now, treat the CLI as one top-level operator tool with subsystem subcommand groups rather than one separate CLI per subsystem.

## Web API implications

Because the system is service-oriented and remote-capable, the API should expose both subsystem and instrument views.

Recommended API groups:

- `/api/v1/instrument/*`
- `/api/v1/daq/*`
- `/api/v1/sensors/*`
- `/api/v1/gas/*`
- `/api/v1/thermal/*`
- `/api/v1/power/*`

Recommended streaming topics:

- instrument state
- subsystem states
- alarms and interlocks
- telemetry
- DAQ metrics
- debug streams

## Data model implications

The system needs more than DAQ data contracts.

Shared contract categories should include:

- telemetry sample
- alarm event
- interlock event
- subsystem health summary
- instrument readiness summary
- command result
- DAQ raw-stream metadata

This argues for expanding `protocol/` beyond only the DAQ wire format into service and pipeline schemas.

## Persistence implications

Persisted data should not only cover DAQ raw stream.

You will likely also need:

- timestamped environmental telemetry
- gas control history
- voltage supply history
- alarm and interlock log
- run-to-environment correlation metadata

These are important for detector performance analysis and post-run diagnosis.

## Recommended next design steps

1. define the instrument-level state machine
2. define normalized subsystem health and alarm schemas
3. define RS485 bus manager ownership and configuration model
4. define interlock policy categories: block-start, degrade, emergency-stop
5. define how DAQ run metadata is joined with environment and power telemetry

## Design rule summary

The detector should be modeled as:

- one instrument
- multiple subsystem services
- one higher-level orchestrator
- explicit coordination and interlock policy

`daq/` remains critical, but it is not the whole system.
