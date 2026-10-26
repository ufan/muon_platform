# ADR-014 Hardware domains: slow-control transports

Status: Accepted (2026-10-25; owner answers in discussion). Refactored 2026-10-26 to remove overlap
with ADR-003; the decision is unchanged. Content confirmed by owner 2026-10-26.
Related: [ADR-003](ADR-003_hardware_domains_services_and_controllers.md) (domain services and controllers, DAQ link)

## Context

Every current slow-control device is a Modbus RTU slave on RS-485, grouped on host ports by assembly
convenience with distinct slave IDs on a shared port. The present host has three RS-485 ports, not
all necessarily used; a future host may be a single-board computer with fewer. Custom HV, LV and gas
boards with on-board domain controllers are planned and will speak Modbus RTU first. A custom
protocol (IMB) and later CAN-FD are aspirations.

## Decision

ADR-003 fixes the service and controller layers; this ADR decides how controllers reach devices.

1. **Transport is configuration.** A versioned device map gives, per device or on-board controller,
   the domain, instance, transport and driver. Today the only transport is `modbus-rtu` (port, slave
   ID, device-type register map); `imb` and `can-fd` may be added later. An on-board controller is
   reached through a thin host proxy over its transport. Moving a device between ports, or replacing
   commercial devices with a custom board, changes configuration, not domain services. Port
   assignment is an assembly choice, never a domain boundary.
2. **One bus owner per host port** serialises half-duplex access and may serve several domains. One
   protocol runs on a port at a time.
3. **No fixed port count.** Ports in use and their device names come from host configuration. No
   domain service or controller assumes a port count, a port name or which devices share a port.
   Consolidating onto fewer ports requires slave/node IDs unique per port and a polling load that fits
   the shared bus.

| Stage | Slow-control hardware | Status |
|---|---|---|
| Current | Commercial Modbus RTU devices on up to three host RS-485 ports, grouped freely | in use |
| Next | Custom HV/LV/gas boards with on-board domain controllers, also Modbus RTU | planned |
| Later | IMB protocol for custom controllers, then IMB on CAN-FD | aspiration; not designed, no trigger |

Not decided here: the IMB protocol (the [management-bus draft](../design/instrument_management_bus.md)
is an input, not a baseline); the device-map format, Modbus library and adapter code structure (the
instrument iteration).

## Consequences

- Domain services can be built now on Modbus host adapters and simulators and survive the move to
  custom boards and any later protocol.
- Where the domain controller is a host adapter, protection that must survive a host or bus failure
  has to come from the device's own built-in protection; the adapter's interlocks cover only what the
  host can enforce.
- Each additional transport needs a bus-owner implementation and device-map support, not a change in
  domain services.

## Alternatives

- **One shared bus now:** rejected; current devices are freely grouped Modbus slaves on several ports.
- **Committing to the IMB protocol now:** deferred; no custom board exists yet and Modbus RTU comes first.
