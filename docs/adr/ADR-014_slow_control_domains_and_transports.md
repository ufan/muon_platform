# ADR-014 Slow-control domains and transports

Status: Accepted (2026-10-25; owner answers in discussion)
Related: [ADR-003](ADR-003_instrument_service_architecture.md) (domain services), [ADR-005](ADR-005_hardware_abstraction.md) (domain controllers)

## Context

The documents disagreed on the slow-control bus. One design note described three RS-485/Modbus buses,
the management-bus draft proposed one RS-485 bus with COBS/protobuf and a DAQ node, ADR-005 favoured
Modbus for gas and sensors and CAN-FD for distributed control, and engineering context expected one
shared bus. None separated current hardware from intent.

Facts from the owner: every current subsystem device is a Modbus RTU slave on RS-485. Devices are grouped
on host ports by assembly convenience, with distinct slave IDs on a shared port. The present host has
three RS-485 ports, not all necessarily used; a future host may be a single-board computer with fewer.
Custom HV, LV and gas boards with on-board domain controllers are planned; they will speak Modbus RTU
first. A custom protocol (IMB) and later CAN-FD are aspirations. Domains with and without a dedicated
controller will coexist for a long time.

## Decision

Slow control is layered: **domain service → domain controller → transport → devices.**

1. **The domain service interface is the stable contract.** Each slow-control domain (HV, LV, gas,
   environment, pose) exposes typed operations plus the common lifecycle, health, alarms and
   capabilities (the domain-service pattern staged in `core/contracts/system/`). It is designed now
   and never changes because a transport or controller form changes.
2. **The domain controller owns control logic, safety and interlocks.** It takes one of two forms,
   both behind the same service interface:
   - a host software adapter that drives the domain's devices directly;
   - a physical on-board controller, reached through a thin host proxy.

   Orchestration software (instrument, applications) never addresses devices; only domain
   controllers do.
3. **Transport is configuration.** A versioned device map gives, per device or controller, the domain,
   instance, transport and driver. Today the only transport is `modbus-rtu` (port, slave ID,
   device-type register map); `imb` and `can-fd` may be added later. Moving a device between ports, or
   replacing commercial devices with a custom board, changes configuration, not domain services.
   Port assignment is an assembly choice, never a domain boundary.
4. **One bus owner per host port** serialises half-duplex access and may serve several domains. One
   protocol runs on a port at a time.
5. **No fixed port count.** Ports in use and their device names come from host configuration. No
   domain service or controller assumes a port count, a port name or which devices share a port.
   Consolidating onto fewer ports requires slave/node IDs unique per port and a polling load that fits
   the shared bus.
6. **DAQ is not on a slow-control bus.** DAQ control, status and scientific data use its dedicated
   link (USB today; possibly another, always separate).
7. **Cooling and dehumidification are out of scope.**

| Stage | Slow-control hardware | Status |
|---|---|---|
| Current | Commercial Modbus RTU devices on up to three host RS-485 ports, grouped freely | in use |
| Next | Custom HV/LV/gas boards with on-board domain controllers, also Modbus RTU | planned |
| Later | IMB protocol for custom controllers, then IMB on CAN-FD | aspiration; not designed, no trigger |

Not decided here: the IMB protocol (the [management-bus draft](../design/instrument_management_bus.md)
is an input, not a baseline); the device-map format, Modbus library and adapter code structure (the
instrument iteration).

## Consequences

- Domain service interfaces can be designed and implemented now against Modbus host adapters and
  simulators, and survive the move to custom boards and any later protocol.
- Where the domain controller is a host adapter, protection that must survive a host or bus failure
  has to come from the device's own built-in protection; the adapter's interlocks cover only what the
  host can enforce. Each domain specification states which applies.
- Each additional transport needs a bus-owner implementation and device-map support, not a change in
  domain services.

## Alternatives considered

- **One shared bus now:** rejected; current devices are freely grouped Modbus slaves on several ports.
- **Commercial devices only behind physical controllers:** rejected; not every domain gets a board.
- **Committing to the IMB protocol now:** deferred; no custom board exists yet and Modbus RTU comes first.
