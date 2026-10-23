# Muography Instrument Platform Architecture Specification

Version: 1.0

## 1. Purpose

This document is the master architecture specification for the planned
muography instrument platform.

It consolidates:

-   product vision
-   application landscape
-   hardware architecture
-   software architecture
-   reconstruction platform
-   data architecture
-   simulation strategy
-   deployment strategy
-   AI-assisted engineering workflow

This document is intended to be the top-level context for:

-   engineering development
-   AI coding agents
-   future team members
-   suppliers
-   software/hardware contractors

------------------------------------------------------------------------

# 2. Platform Vision

The product is not only a detector.

It is a complete scientific sensing platform:

    Detector Hardware

    +

    Embedded Control

    +

    Scientific Reconstruction

    +

    Data Platform

    +

    Digital Twin

    +

    Engineering Application

The core value is created by:

-   detector technology
-   reconstruction algorithms
-   accumulated datasets
-   application-specific models
-   engineering workflows

------------------------------------------------------------------------

# 3. Application Landscape

Primary application domains:

## Underground Engineering

Examples:

-   TBM advance geological prediction
-   tunnel anomaly detection

Outputs:

-   density anomaly
-   geological risk indication

------------------------------------------------------------------------

## Civil Infrastructure

Examples:

-   dam health monitoring
-   internal erosion monitoring
-   foundation anomaly detection

Outputs:

-   density evolution
-   structural risk indicators

------------------------------------------------------------------------

## Industrial Inspection

Examples:

-   blast furnaces
-   large reactors
-   storage structures

Outputs:

-   internal density distribution
-   process information

------------------------------------------------------------------------

# 4. Overall Platform Architecture

                         Applications

            GUI / Cloud / AI / Digital Twin


                               |

                        Data Products


                               |

                  Scientific Computing Platform


           Reconstruction
           Density Inversion
           AI Interpretation


                               |

                  Instrument Software Platform


           Service Layer

           DAQ
           HV
           Gas
           Pose
           Health


                               |

                        Hardware Layer

           FPGA
           STM32
           Micromegas Detector

------------------------------------------------------------------------

# 5. Hardware Architecture

The instrument consists of independent domains.

## DAQ Domain

Responsibilities:

-   detector readout
-   FPGA processing
-   event generation

------------------------------------------------------------------------

## HV Domain

Responsibilities:

-   0-2000V supply
-   current monitoring
-   protection

------------------------------------------------------------------------

## Gas Domain

Responsibilities:

-   gas control
-   flow regulation
-   pressure monitoring

------------------------------------------------------------------------

## Pose Domain

Responsibilities:

-   orientation
-   position
-   motion control

------------------------------------------------------------------------

## Central Controller

Responsibilities:

-   data fusion
-   reconstruction
-   orchestration
-   communication
-   user interaction

------------------------------------------------------------------------

# 6. Service Architecture

Hardware domains expose services.

    Hardware

       |

    Firmware Controller

       |

    Service API

       |

    Central Software

Recommended interfaces:

-   gRPC/protobuf
-   Zenoh where distributed communication is required

Avoid:

-   direct register access from applications
-   hardware-specific logic leakage

------------------------------------------------------------------------

# 7. Reconstruction Architecture

The reconstruction pipeline is a scientific dataflow system.

It is NOT decomposed into microservices.

    Reconstruction Service


            Taskflow Runtime


            Decoder

               |

            Hit Reconstruction

               |

            Cluster Reconstruction

               |

            Track Reconstruction

               |

            Physics Products

------------------------------------------------------------------------

# 8. Muon EDM

The Muon EDM is the central scientific contract.

Main objects:

    MuonEvent

        RawHits

        Hits

        Clusters

        Tracks

        Conditions

Rules:

-   algorithms communicate only through EDM
-   serialization is outside algorithms
-   provenance is mandatory

------------------------------------------------------------------------

# 9. Data Architecture

Four data layers:

    Raw Binary Data

            |

    Muon EDM

            |

    Online Data Products

            |

    Analytics Storage

------------------------------------------------------------------------

## Raw Data

Properties:

-   immutable
-   versioned
-   long-term archive

------------------------------------------------------------------------

## Online Data Products

Examples:

-   tracks
-   hit maps
-   count rates
-   density estimates

------------------------------------------------------------------------

## Analytics Storage

Recommended:

-   Arrow
-   Parquet

------------------------------------------------------------------------

# 10. Acquisition Architecture

The acquisition layer supports three sources:

                     Acquisition Service


            +------------+-------------+

            |            |             |

          Live        Replay       Simulation

          DAQ         Backend      Backend


            +------------+-------------+

                         |

                  Unified Raw Stream

------------------------------------------------------------------------

# 11. Replay Platform

Replay is a first-class engineering capability.

Functions:

-   algorithm development
-   regression testing
-   customer demonstration
-   AI dataset generation

The reconstruction chain must run identically on:

-   real data
-   replay data
-   simulation data

------------------------------------------------------------------------

# 12. Simulation Platform

Simulation provides the digital engineering loop.

    Geometry

       |

    Density Field

       |

    Muon Simulation

       |

    DAQ Simulation

       |

    Raw Data

       |

    Reconstruction

       |

    Validation

Tools:

-   Geant4
-   fast simulation
-   FreeCAD/OpenSCAD
-   VTK/ParaView

------------------------------------------------------------------------

# 13. Digital Twin Architecture

Digital twin connects:

    Physical Object

    +

    Measurement System

    +

    Scientific Data

    +

    Engineering Decision

Layers:

1.  Geometry
2.  Detector deployment
3.  Measurement data
4.  Density field
5.  Engineering interpretation

------------------------------------------------------------------------

# 14. Deployment Architecture

Target:

Linux ARM64 edge appliance.

Initial deployment:

    systemd

    +

    Deb packages

    +

    CI/CD

Production roadmap:

    RAUC/Mender OTA

    +

    Fleet Management

------------------------------------------------------------------------

# 15. Development Workflow

AI-assisted engineering model:

    Human Architecture

            |

    AI Coding Agents

            |

    CI/CD Validation

            |

    Simulation Testing

            |

    Hardware Validation

            |

    Product Release

------------------------------------------------------------------------

# 16. Repository Philosophy

> **Superseded by [ADR-012](../adr/ADR-012_repository_baseline_and_workflow.md)** (2026-10-23):
> one repository per domain (`muon_core` is the scientific domain), with an instrument layer above. The
> list below is a historical sketch of domains, not the repository layout.

Recommended:

    muon-platform/

    hardware/

    firmware/

    services/

    reconstruction/

    muon_edm/

    simulation/

    datasets/

    digital_twin/

    deployment/

    docs/

------------------------------------------------------------------------

# 17. AI Coding Agent Rules

Agents must:

1.  Respect architecture boundaries.
2.  Never bypass EDM contracts.
3.  Keep hardware isolated behind services.
4.  Support replay testing.
5.  Preserve ARM64 compatibility.
6.  Prefer existing libraries.
7.  Update architecture documents with major changes.
8.  Avoid unnecessary frameworks.

------------------------------------------------------------------------

# 18. Technology Stack Summary

## Embedded

-   STM32
-   Zephyr RTOS
-   FPGA

## Edge Computing

-   Linux ARM64
-   C++
-   Taskflow
-   gRPC
-   protobuf

## Data

-   Muon EDM
-   Arrow
-   Parquet

## Visualization

-   Qt/QML
-   VTK
-   ParaView

## Simulation

-   Geant4
-   custom fast simulation

## Deployment

-   CMake
-   Conan/vcpkg
-   CI/CD
-   systemd

------------------------------------------------------------------------

# 19. Final Architecture Decision

The muography instrument shall be developed as:

    Scientific Instrument Platform

            =

    Hardware Platform

    +

    Service-Oriented Control

    +

    EDM-Based Reconstruction

    +

    Data Replay and Simulation

    +

    Digital Twin

    +

    AI-Assisted Engineering

This architecture is optimized for:

-   one-person deep-tech company
-   long product lifetime
-   multiple instrument variants
-   continuous algorithm evolution
-   industrial deployment
