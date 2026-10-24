# Muography Instrument Platform

# System Architecture Specification

Version: 1.0

------------------------------------------------------------------------

# 1. Purpose and Scope

This document defines the system-level architecture of the planned
muography instrument platform.

It provides the stable architecture reference connecting:

-   product requirements
-   hardware architecture
-   firmware architecture
-   instrument services
-   reconstruction software
-   data architecture
-   simulation environment
-   digital twin applications
-   deployment strategy

This document is intended to be the primary context document for:

-   engineers
-   suppliers
-   future team members
-   AI coding agents

------------------------------------------------------------------------

# 2. Architecture Principles

The platform follows these principles:

## 2.1 Modular Scientific Instrument Architecture

The instrument is not a single embedded device.

It is a collection of independent technical domains:

    Detector

    DAQ

    HV

    Gas

    Pose

    Computing

    Software Platform

Each domain has:

-   clear responsibility
-   stable interface
-   independent evolution

------------------------------------------------------------------------

## 2.2 Separation of Control Plane and Data Plane

The architecture separates:

## Control Plane

Responsible for:

-   hardware control
-   configuration
-   health monitoring
-   instrument state

Examples:

    HV Service

    Gas Service

    Pose Service

    DAQ Service

    Health Service

------------------------------------------------------------------------

## Data Plane

Responsible for:

-   high-rate scientific data processing

Examples:

    Raw Data

    Muon EDM

    Reconstruction

    Physics Products

------------------------------------------------------------------------

# 3. System Context

The instrument operates as a scientific sensing platform.

                    Users

     Engineering Team
     Field Operator
     Customer


                        |

                        |

              Muography Instrument


                        |

                        |

           Cloud / Data Platform


                        |

                        |

           Engineering Database

------------------------------------------------------------------------

# 4. Overall System Architecture

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


            +------------+------------+------------+

            DAQ        HV          Gas        Pose

            Service    Service     Service    Service


                                   |

                    Hardware Domain Controllers


            FPGA       STM32      STM32      MCU


                                   |

                       Micromegas Detector

------------------------------------------------------------------------

# 5. Hardware Architecture

The hardware platform consists of independent domain controllers.

------------------------------------------------------------------------

# 5.1 DAQ Controller

Responsibilities:

-   detector readout
-   FPGA data processing
-   event generation
-   timestamp generation

Architecture:

    Micromegas Detector

            |

    Front-end Electronics

            |

    FPGA

            |

    DAQ Controller

            |

    DAQ Service

The DAQ controller is a peer domain controller, not a passive
peripheral.

------------------------------------------------------------------------

# 5.2 High Voltage Controller

Responsibilities:

-   detector bias generation
-   voltage ramping
-   current monitoring
-   protection

Target:

-   0-2000V output
-   sub-nanoamp current measurement

Architecture:

    HV Module

        |

    STM32 Controller

        |

    HV Service

------------------------------------------------------------------------

# 5.3 Gas Controller

Responsibilities:

-   gas flow regulation
-   pressure monitoring
-   environmental monitoring

Architecture:

    Sensors

     |

    STM32

     |

    Gas Service

------------------------------------------------------------------------

# 5.4 Pose Controller

Responsibilities:

-   orientation measurement
-   global position
-   future motion control

Architecture:

    IMU/GNSS

     |

    Controller

     |

    Pose Service

------------------------------------------------------------------------

# 5.5 Central Controller

Responsibilities:

-   data fusion
-   reconstruction
-   orchestration
-   communication
-   user interaction

Target:

-   ARM64 Linux SoM

------------------------------------------------------------------------

# 6. Software Architecture

The software architecture consists of five layers.

------------------------------------------------------------------------

# Layer 0: Hardware

Components:

-   Micromegas detector
-   FPGA
-   STM32 controllers
-   sensors
-   power systems

------------------------------------------------------------------------

# Layer 1: Firmware

Responsibilities:

-   deterministic control
-   hardware abstraction
-   safety functions
-   communication

Technology:

-   Zephyr RTOS
-   FPGA firmware

------------------------------------------------------------------------

# Layer 2: Instrument Service Layer

The service layer abstracts hardware.

Architecture:

    Hardware

       |

    Firmware

       |

    Service API

       |

    Central Software

Recommended technologies:

-   protobuf
-   gRPC
-   Zenoh optional

Services:

    DAQ Service

    HV Service

    Gas Service

    Pose Service

    Health Service

    Configuration Service

------------------------------------------------------------------------

# Layer 3: Scientific Computing Platform

The reconstruction system is an internal dataflow pipeline.

Architecture:

    Acquisition

          |

    Muon EDM

          |

    Taskflow Runtime

          |

    Algorithms

          |

    Physics Products

Algorithms are modules, not microservices.

------------------------------------------------------------------------

# Layer 4: Applications

Examples:

-   Qt/QML GUI
-   cloud dashboard
-   digital twin
-   AI analytics

------------------------------------------------------------------------

# 7. Data Architecture

The data architecture follows:

    Raw Data

       |

    Muon EDM

       |

    Reconstruction

       |

    Data Products

       |

    Analytics Storage

------------------------------------------------------------------------

# 7.1 Acquisition Sources

The system supports three acquisition backends.

                    Acquisition Service


           +-------------+-------------+

           |             |             |

        Live DAQ      Replay      Simulation

        Backend       Backend      Backend


           +-------------+-------------+

                         |

                  Unified Raw Stream

------------------------------------------------------------------------

# 7.2 Raw Data

Properties:

-   immutable
-   versioned
-   reproducible

Contains:

-   detector packets
-   timestamps
-   metadata

------------------------------------------------------------------------

# 7.3 Muon EDM

Scientific data contract.

Objects:

    MuonEvent

    RawHit

    Hit

    Cluster

    Track

    Conditions

All algorithms communicate through EDM.

------------------------------------------------------------------------

# 8. Reconstruction Architecture

The reconstruction engine uses a DAG model.

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

Design principles:

-   modular algorithms
-   configurable pipeline
-   replay validation
-   ARM64 compatible

------------------------------------------------------------------------

# 9. Replay and Simulation Architecture

The platform maintains a digital validation loop.

    Geometry Model

          |

    Density Field

          |

    Muon Simulation

          |

    DAQ Simulation

          |

    Raw Data

          |

    Replay/Reconstruction

          |

    Digital Twin

Replay is a first-class engineering capability.

Uses:

-   algorithm development
-   regression testing
-   customer demonstrations
-   AI dataset generation

------------------------------------------------------------------------

# 10. Digital Twin Architecture

The digital twin connects:

    Physical Object

    +

    Detector Deployment

    +

    Measurement Data

    +

    Density Reconstruction

    +

    Engineering Decision

Layers:

1.  Geometry
2.  Detector placement
3.  Measurement data
4.  Density field
5.  Engineering interpretation

------------------------------------------------------------------------

# 11. Deployment Architecture

Target platform:

-   Linux ARM64

Development:

-   x86_64

Deployment:

    Application

     |

    systemd service

     |

    ARM64 Linux

Initial:

-   Debian packages

Future:

-   RAUC/Mender OTA

------------------------------------------------------------------------

# 12. Development Architecture

Recommended repository:

    muon-platform/

    docs/

    hardware/

    firmware/

    services/

    reconstruction/

    muon_edm/

    simulation/

    datasets/

    digital_twin/

    deployment/

    tests/

------------------------------------------------------------------------

# 13. Technology Stack

  Domain          Technology
  --------------- ----------------
  MCU Firmware    Zephyr
  Embedded MCU    STM32
  FPGA            FPGA-based DAQ
  OS              Linux ARM64
  Language        C++20
  Build           CMake
  Dependency      Conan/vcpkg
  Runtime         Taskflow
  API             gRPC/protobuf
  Messaging       Zenoh optional
  EDM             Muon EDM
  Storage         Arrow/Parquet
  Visualization   Qt/QML, VTK
  Simulation      Geant4/FastSim

------------------------------------------------------------------------

# 14. AI Coding Agent Context

AI agents shall use this document as the system architecture reference.

Rules:

1.  Respect hardware/software boundaries.
2.  Never bypass service interfaces.
3.  Never bypass Muon EDM.
4.  Reconstruction algorithms are not microservices.
5.  Every acquisition feature supports replay.
6.  Every component must support testing.
7.  Architecture changes require ADR updates.

------------------------------------------------------------------------

# 15. Final Architecture Statement

The muography instrument platform is designed as:

    Scientific Instrument

    =

    Modular Hardware Domains

    +

    Service-Oriented Control

    +

    EDM-Based Reconstruction

    +

    Replay and Simulation Platform

    +

    Digital Twin

    +

    AI-Assisted Engineering

This architecture supports evolution from prototype instruments to
scalable commercial scientific products.
