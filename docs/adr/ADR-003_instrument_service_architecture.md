# ADR-003 Instrument Service Architecture

## Decision

Use service-oriented boundaries between hardware domains and central software.

Domains:

- DAQ
- HV
- Gas
- Pose
- Health

## Architecture

Hardware

|

Firmware

|

Service API

|

Central Controller

## Interface

Preferred:

- protobuf
- gRPC

Optional:

- Zenoh

## Principle

Hardware exposes capabilities, not registers.

Applications never directly access hardware.
