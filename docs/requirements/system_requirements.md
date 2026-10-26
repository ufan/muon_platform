# Product and system requirements

Status: draft. Product context (§1–§3) and the agreed top-level requirements (§4–§7). Each domain
adds IDs (`SYS-NNN`, `HV-NNN`, …), numeric targets and acceptance criteria when it enters its
iteration ([ADR-010 §7](../adr/ADR-010_spec_driven_domain_iteration.md#7-requirement-ids)). How
the system meets them is in the [system architecture](../architecture/system_architecture.md).
Merged 2026-10-25 with the former `product_landscape.md` (full text in git).

## 1. Product

A portable scientific sensing instrument for non-invasive density imaging and structural
monitoring of large objects. Micromegas gaseous detectors track natural cosmic-ray muons; dense
regions absorb more of them, so the angular muon flux behind an object reveals its density:

```text
muon -> detector telescope -> trajectories -> angular flux -> density inversion -> 3D density
```

Compared with conventional inspection it is passive, penetrates large volumes and can monitor for
years. The product is a complete sensing system (detector, embedded control, reconstruction, data
platform, interpretation), and its long-term value lies in reconstruction algorithms,
application-specific models, accumulated data and engineering workflows.

## 2. Applications

| Application | Questions answered | Products |
|---|---|---|
| TBM advance geological prediction | geology ahead of the cutter head: cavities, water-bearing zones, abnormal structures | density anomaly map, risk indicator, prediction report |
| Dam and civil infrastructure monitoring | seepage, internal erosion, density degradation, voids, foundation anomalies | density distribution, anomaly evolution, digital twin update |
| Large industrial equipment (blast furnaces) | burden distribution, material density, internal wear of inaccessible hot interiors | density maps |
| Large storage structures (tanks, silos, reactors) | filling distribution, density changes, abnormal regions | density maps |
| Geological exploration and research | subsurface density structure | density models, datasets |

## 3. Deployment modes and roadmap

| Mode | Installation | Processing | Workflow |
|---|---|---|---|
| Survey | mobile, short-term, one or several sites, optimized geometry | offline reconstruction | deploy → acquire → reconstruct → engineering evaluation |
| Continuous monitoring | fixed, long-term, unattended, one or several sites, cloud connection | online reconstruction, quasi-real-time reports over a moving time window | stream → reconstruct → trend analysis → warning |

| Generation | Focus |
|---|---|
| 1 | reliable detector operation, manual deployment, offline reconstruction |
| 2 | online reconstruction, remote monitoring, automated diagnostics |
| 3 | multi-instrument deployment, cloud analytics, AI-assisted interpretation |

## 4. Functions

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
6. process live and replayed data identically;
7. record, for every scientific product, the instrument, firmware, detector configuration, geometry,
   calibration, algorithm and software versions, and time.

## 5. Operation and lifecycle

The system shall:

1. run unattended, recover through watchdogs, report faults, allow remote diagnostics and shut
   down safely; HV safety, gas safety and DAQ data integrity are critical;
2. support several instrument variants and independent subsystem upgrades;
3. change configuration without recompiling;
4. manage manufacturing configuration, calibration, software and firmware updates, and deployment
   records.

## 6. Constraints

- Linux; development on x86_64, deployment on ARM64.

## 7. Performance

To be defined per domain: detector event rate, reconstruction throughput, processing latency, data
and storage bandwidth, CPU use. Example HV range (not an acceptance limit): 0–2000 V with sub-nA
current measurement.
