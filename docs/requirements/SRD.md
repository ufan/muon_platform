# Muography Instrument Platform

# System Requirements Document (SRD)

Status: draft. Imported baseline without requirement IDs; IDs (`SYS-NNN`, `HV-NNN`, …) are assigned as each domain enters its iteration ([ADR-010 §7](../adr/ADR-010_spec_driven_domain_iteration.md#7-requirement-ids)). “Example target” values are illustrative, not acceptance limits. Technology and process sections defer to [system architecture](../architecture/system_architecture.md) and `AGENTS.md`.

Version: 1.0

------------------------------------------------------------------------

# 1. Document Purpose

This document defines the top-level system requirements for the
muography instrument platform.

It specifies:

-   product objectives
-   application scenarios
-   system capabilities
-   functional requirements
-   performance requirements
-   hardware/software constraints
-   data requirements
-   verification strategy

This document is the engineering baseline for:

-   architecture decisions
-   hardware design
-   firmware development
-   software development
-   AI-assisted coding workflows
-   productization

------------------------------------------------------------------------

# 2. Product Overview

## 2.1 Product Definition

The muography instrument platform is a scientific sensing system based
on Micromegas detector technology.

The system uses naturally occurring cosmic-ray muons to measure material
transmission and reconstruct density information of large-scale objects.

The platform consists of:

    Detector Hardware

    +

    Embedded Control Electronics

    +

    Scientific Reconstruction Software

    +

    Data Platform

    +

    Digital Twin Applications

------------------------------------------------------------------------

# 3. Mission Statement

The system shall provide:

-   non-invasive density imaging
-   long-term structural monitoring
-   underground geological investigation
-   industrial process observation

The product value is created through:

-   reliable detector operation
-   high-quality reconstruction algorithms
-   application-specific interpretation
-   accumulated measurement datasets

------------------------------------------------------------------------

# 4. Target Applications

## 4.1 TBM Advance Geological Prediction

### Objective

Provide information about geological conditions ahead of tunnel
excavation.

### Requirements

The system shall support:

-   mobile deployment
-   detector pose tracking
-   forward-looking reconstruction
-   anomaly indication

Outputs:

-   density anomaly maps
-   geological risk indicators

------------------------------------------------------------------------

## 4.2 Dam Structural Health Monitoring

### Objective

Monitor large concrete structures over their lifecycle.

Requirements:

-   continuous operation
-   environmental compensation
-   density evolution monitoring
-   anomaly visualization

Outputs:

-   density field
-   structural indicators
-   digital twin updates

------------------------------------------------------------------------

## 4.3 Industrial Inspection

Examples:

-   blast furnaces
-   reactors
-   large storage structures

Requirements:

-   non-invasive measurement
-   internal state estimation
-   inaccessible volume inspection

------------------------------------------------------------------------

# 5. System Architecture Requirements

The system shall consist of:

    Application Layer

            |

    Data Product Layer

            |

    Scientific Computing Layer

            |

    Instrument Service Layer

            |

    Hardware Domain Layer

            |

    Detector Hardware

------------------------------------------------------------------------

# 6. Functional Requirements

# 6.1 Detector Data Acquisition

The system shall:

-   acquire detector raw data
-   preserve original binary data
-   timestamp events
-   support continuous acquisition
-   provide acquisition status information

------------------------------------------------------------------------

# 6.2 High Voltage Control

The system shall:

-   generate detector bias voltage
-   support controlled voltage ramping
-   measure output voltage
-   measure detector current
-   provide protection mechanisms

Example target (illustrative, not an acceptance limit; see system architecture §10):

-   voltage range: 0-2000V
-   current measurement: sub-nanoamp capability

------------------------------------------------------------------------

# 6.3 Gas Control

The system shall:

-   control gas flow
-   monitor pressure
-   monitor environmental parameters
-   support automatic regulation

------------------------------------------------------------------------

# 6.4 Pose and Motion Control

The system shall:

-   measure detector orientation
-   provide position information
-   support future motion control

------------------------------------------------------------------------

# 6.5 Reconstruction

The system shall support:

    Raw Binary

        |

    Decode

        |

    Hit Reconstruction

        |

    Cluster Reconstruction

        |

    Track Reconstruction

        |

    Physics Data Products

Generated products include:

-   hits
-   clusters
-   tracks
-   count rates
-   angular maps
-   density reconstruction inputs

------------------------------------------------------------------------

# 6.6 Data Replay

The system shall support replay of previously acquired raw datasets.

Replay shall support:

-   algorithm development
-   regression testing
-   demonstration
-   AI dataset generation

The reconstruction pipeline shall operate identically on:

-   live acquisition
-   replay data
-   simulation data

------------------------------------------------------------------------

# 6.7 Simulation

The system shall support:

-   detector simulation
-   synthetic data generation
-   algorithm validation
-   performance evaluation

Simulation outputs shall be compatible with real acquisition formats.

------------------------------------------------------------------------

# 7. Hardware Requirements

## 7.1 Domain Controller Architecture

The instrument shall use independent hardware domains:

-   DAQ controller
-   HV controller
-   gas controller
-   pose controller

Each domain shall:

-   perform deterministic local control
-   expose stable interfaces
-   isolate hardware details

------------------------------------------------------------------------

## 7.2 Central Controller

The central controller shall provide:

-   data fusion
-   reconstruction
-   orchestration
-   external communication
-   user interaction

Target:

-   ARM64 Linux platform

------------------------------------------------------------------------

# 8. Software Requirements

## 8.1 Operating System

Required:

-   Linux

Development:

-   x86_64

Deployment:

-   ARM64

------------------------------------------------------------------------

## 8.2 Software Architecture

The system shall support:

-   service-oriented hardware control
-   EDM-based reconstruction
-   configurable pipelines
-   replay-based testing
-   simulation-based validation

------------------------------------------------------------------------

## 8.3 Reconstruction Runtime

The reconstruction engine shall support:

-   modular algorithms
-   DAG execution
-   online processing
-   future algorithm replacement

Initial implementation:

-   Taskflow-based runtime

------------------------------------------------------------------------

# 9. Data Requirements

## 9.1 Raw Data

Raw data shall be:

-   immutable
-   archived
-   versioned
-   reproducible

Metadata shall include:

-   instrument version
-   firmware version
-   detector configuration
-   geometry version
-   calibration version

------------------------------------------------------------------------

## 9.2 Reconstruction Data

Data products shall include:

-   reconstructed tracks
-   detector performance metrics
-   angular distributions
-   density products

------------------------------------------------------------------------

## 9.3 Data Provenance

Every scientific result shall record:

    instrument_version

    geometry_version

    calibration_version

    algorithm_version

    software_version

    timestamp

------------------------------------------------------------------------

# 10. Communication Requirements

These are technology preferences and candidates, not acceptance requirements. Current direction
and open topology questions: system architecture §3, §8 and §10.

The system shall support:

## Internal services

Preferred:

-   gRPC
-   protobuf

Optional:

-   Zenoh

## Hardware communication

Possible:

-   RS485
-   Modbus RTU
-   CAN-FD
-   Ethernet

Selection depends on subsystem requirements. Selected approach: [ADR-014](../adr/ADR-014_slow_control_domains_and_transports.md) (Modbus RTU now; custom protocol and CAN-FD are aspirations).

------------------------------------------------------------------------

# 11. Performance Requirements

The system shall define measurable targets for:

  Parameter                   Target
  --------------------------- --------
  Detector event rate         TBD
  Reconstruction throughput   TBD
  Processing latency          TBD
  Data bandwidth              TBD
  Storage bandwidth           TBD
  CPU utilization             TBD

------------------------------------------------------------------------

# 12. Reliability Requirements

The system shall support:

-   unattended operation
-   watchdog recovery
-   fault reporting
-   remote diagnostics
-   safe shutdown

Critical subsystems:

-   HV safety
-   gas safety
-   DAQ integrity

------------------------------------------------------------------------

# 13. Maintainability Requirements

The platform shall support:

-   multiple instrument variants
-   independent subsystem upgrades
-   algorithm replacement
-   configuration changes without recompilation
-   long-term software maintenance

------------------------------------------------------------------------

# 14. Verification and Validation

Validation shall follow:

    Requirement

        |

    Test Case

        |

    Simulation

        |

    Replay Dataset

        |

    Hardware Validation

Testing layers:

-   unit testing
-   integration testing
-   replay regression testing
-   hardware-in-loop testing

------------------------------------------------------------------------

# 15. Product Lifecycle Requirements

The system shall support:

-   manufacturing configuration
-   calibration management
-   software updates
-   firmware updates
-   deployment tracking
-   customer maintenance

------------------------------------------------------------------------

# 16. AI-Assisted Engineering Requirements

Engineering-process rules for AI agents are not product requirements. They are maintained in
`platform/AGENTS.md` and `platform/docs/engineering_context.md`; this section intentionally holds
no separate rule list.

------------------------------------------------------------------------

# 17. Traceability to Architecture Decisions

  Requirement Area         ADR
  ------------------------ --------
  Reconstruction runtime   ADR-001
  EDM and serialization    ADR-002
  Service architecture     ADR-003
  Deployment               ADR-004
  Hardware abstraction     ADR-005
  AI workflow              ADR-006
  Digital twin             ADR-007
  Simulation and replay    ADR-008

------------------------------------------------------------------------

# 18. Final System Requirement Statement

The muography instrument platform shall be developed as a modular
scientific instrument system combining:

    Advanced Detector Hardware

    +

    Embedded Domain Controllers

    +

    Service-Oriented Control

    +

    EDM-Based Reconstruction

    +

    Replay and Simulation Platform

    +

    Digital Twin Applications

The system shall enable continuous evolution from prototype instruments
to scalable commercial products.
