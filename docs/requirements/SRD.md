# System requirements (SRD)

Status: draft. These are the agreed top-level requirements. Each domain adds IDs (`SYS-NNN`,
`HV-NNN`, …), numeric targets and acceptance criteria when it enters its iteration
([ADR-010 §7](../adr/ADR-010_spec_driven_domain_iteration.md#7-requirement-ids)). How the system
meets them is in the [system architecture](../architecture/system_architecture.md).

## 1. Product

A portable muography instrument: Micromegas detectors measure the transmission of natural
cosmic-ray muons to infer the density of large objects, non-invasively.

- **Applications:** advance geological prediction for tunnel boring machines (TBM); dam and civil
  infrastructure monitoring; inspection of large industrial structures (blast furnaces, reactors,
  storage); geological exploration; research.
- **Deployment modes:** survey (temporary or mobile, e.g. on a TBM) and continuous monitoring
  (long-term, unattended).

## 2. Functions

The system shall:

1. acquire detector data continuously, keep the raw data byte-exact and immutable, timestamp it and
   report acquisition status;
2. generate and ramp the detector bias voltage, measure voltage and current, and protect the
   detector and supply;
3. regulate gas flow, monitor pressure and protect the gas system;
4. measure detector orientation and position, and the operating environment (pressure,
   temperature, humidity);
5. reconstruct hits, clusters and tracks, and produce rates, angular distributions and inputs for
   density reconstruction;
6. process live, replayed and simulated data identically;
7. simulate the detector and produce synthetic data in the real acquisition format;
8. record, for every scientific product, the instrument, firmware, detector configuration, geometry,
   calibration, algorithm and software versions, and time.

## 3. Operation and lifecycle

The system shall:

1. run unattended, recover through watchdogs, report faults, allow remote diagnostics and shut
   down safely; HV safety, gas safety and DAQ data integrity are critical;
2. support several instrument variants and independent subsystem upgrades;
3. change configuration without recompiling;
4. manage manufacturing configuration, calibration, software and firmware updates, and deployment
   records.

## 4. Constraints

- Linux; development on x86_64, deployment on ARM64.

## 5. Performance

To be defined per domain: detector event rate, reconstruction throughput, processing latency, data
and storage bandwidth, CPU use. Example HV range (not an acceptance limit): 0–2000 V with sub-nA
current measurement.
