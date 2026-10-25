# Architecture Decision Report (ADR-08 Updated)

Status: reference. Original option study (2026) behind [ADR-008](../adr/ADR-008_simulation_verification_replay.md); the ADR holds the decision, and later decisions override this text. Its agent-rule and repository-layout sections are obsolete.

# Muography Simulation, Verification and Data Replay Platform

Version: 1.1

# 1. Decision Summary

This document defines the simulation, verification, and data
reproduction architecture for the muography instrument platform.

The platform shall support three equivalent acquisition sources:

1.  Real detector acquisition
2.  Recorded raw data replay
3.  Synthetic simulation

All three sources shall provide the same downstream data interface.

The key decision:

> Reconstruction software must be independent from the physical data
> source.

The reconstruction pipeline consumes a unified event stream regardless
of whether the source is:

-   a Micromegas detector in operation
-   an archived prototype dataset
-   a synthetic simulation environment

------------------------------------------------------------------------

# 2. Motivation

A commercial scientific instrument requires continuous software
evolution.

Direct dependence on hardware creates:

-   slow development cycles
-   limited testing opportunities
-   difficulty reproducing bugs
-   expensive validation

The existing prototype instruments have already generated valuable
real-world raw datasets.

These datasets become a critical engineering asset.

The replay system provides:

-   algorithm development environment
-   regression testing platform
-   customer demonstration capability
-   AI training data source
-   long-term reproducibility

------------------------------------------------------------------------

# 3. Digital Engineering Loop

The complete development loop:

    Physical Instrument

            |

    Raw Data Acquisition

            |

    Raw Data Archive

            |

    Replay / Simulation / Real Acquisition

            |

    Reconstruction Platform

            |

    Muon EDM

            |

    Digital Twin

            |

    Engineering Decision

------------------------------------------------------------------------

# 4. Acquisition Source Abstraction

The acquisition layer shall abstract the origin of data.

Architecture:

                     Acquisition Service


                           |

              +------------+-------------+

              |            |             |

         Live DAQ      Replay        Simulation

         Backend       Backend       Backend


              |            |             |

              +------------+-------------+

                           |

                   Raw Event Stream

                           |

                  Reconstruction

------------------------------------------------------------------------

# 5. DAQ Service Architecture

The DAQ service exposes a common interface.

Example:

``` cpp
class IDataSource
{

public:

virtual bool open() = 0;

virtual bool next(
    RawEvent& event
)=0;

virtual void close() = 0;

};
```

Implementations:

    LiveDAQBackend

        |
        FPGA / USB / Ethernet


    ReplayBackend

        |
        Raw Binary Archive


    SimulationBackend

        |
        Synthetic Generator

------------------------------------------------------------------------

# 6. Replay Service

## 6.1 Purpose

The replay service provides a virtual detector acquisition environment.

It allows the complete software stack to run without hardware.

------------------------------------------------------------------------

## 6.2 Use Cases

### Algorithm Development

Example:

    Raw Dataset

          |

    Hit Reconstruction

          |

    Track Algorithm

          |

    Performance Evaluation

------------------------------------------------------------------------

### Regression Testing

Every software release can run:

    Reference Dataset

          |

    New Reconstruction Version

          |

    Compare Results

Metrics:

-   hit efficiency
-   track efficiency
-   angular resolution
-   reconstruction latency
-   event throughput

------------------------------------------------------------------------

### Customer Demonstration

Example:

    TBM Dataset Replay

            |

    Online Reconstruction

            |

    3D Visualization

No detector deployment required.

------------------------------------------------------------------------

### AI Dataset Generation

Example:

    Raw Archive

          |

    Feature Extraction

          |

    Machine Learning Dataset

------------------------------------------------------------------------

# 7. Replay Fidelity Requirements

The replay service should reproduce realistic acquisition behavior.

It should support:

-   event timestamps
-   trigger structure
-   packet ordering
-   packet loss simulation
-   acquisition rate control
-   detector metadata

Example:

``` yaml
replay:

  file:
    run_001.bin

  mode:
    realtime

  rate:
    1000Hz

  packet_loss:
    0.01
```

------------------------------------------------------------------------

# 8. Raw Data Archive Strategy

Raw data is the scientific ground truth.

Rules:

-   immutable
-   versioned
-   never overwritten
-   independent from reconstruction software

Recommended structure:

    dataset/

     run_001/

        raw.bin

        metadata.yaml

     run_002/

        raw.bin

        metadata.yaml

Metadata:

    instrument_version

    firmware_version

    detector_configuration

    geometry_version

    calibration_version

    timestamp

------------------------------------------------------------------------

# 9. Simulation Platform

Simulation provides synthetic acquisition.

The chain:

    Geometry Model

          |

    Density Field

          |

    Muon Generator

          |

    Detector Response

          |

    DAQ Simulation

          |

    Raw Binary

          |

    Replay/Reconstruction

The simulated output should match real DAQ format.

------------------------------------------------------------------------

# 10. Reconstruction Integration

The reconstruction engine must not know the source.

Architecture:

    DAQ Source

           |

    Raw Event

           |

    Muon EDM

           |

    Taskflow Reconstruction

           |

    Data Products

No reconstruction algorithm should contain:

-   USB access
-   file reading
-   simulation logic

------------------------------------------------------------------------

# 11. Relationship With Digital Twin

Replay enables the digital twin development loop:

    Real Measurement

           |

    Stored Dataset

           |

    Reconstruction

           |

    Density Model Update

           |

    Digital Twin

Historical datasets become reusable digital assets.

------------------------------------------------------------------------

# 12. Verification Strategy

Validation layers:

## Unit Test

Algorithm level:

-   decoder
-   hit reconstruction
-   tracking

## Dataset Regression

Reference raw datasets:

-   known detector runs
-   known reconstruction results

## Simulation Validation

Synthetic truth comparison:

    Truth

     |

    Simulation

     |

    Reconstruction

     |

    Error Analysis

## Hardware-in-loop

Final validation:

    DAQ Hardware

     |

    Controller

     |

    Reconstruction

     |

    Verification

------------------------------------------------------------------------

# 13. Recommended Technical Stack

## Acquisition

-   C++ service abstraction
-   protobuf interfaces
-   raw binary archive

## Simulation

-   Geant4
-   fast muon simulator
-   custom detector response

## Reconstruction

-   Taskflow
-   Muon EDM
-   C++

## Data

-   raw binary
-   protobuf
-   Arrow/Parquet

## Visualization

-   VTK
-   ParaView
-   Qt/QML

------------------------------------------------------------------------

# 14. Repository Structure

Recommended:

    muon-platform/

    acquisition/

        live_daq/

        replay_service/

        simulation_source/


    simulation/

        geometry/

        density_fields/

        muon_generator/


    reconstruction/

        edm/

        algorithms/

        runtime/


    datasets/

        raw/

        reference/


    digital_twin/

    tests/

------------------------------------------------------------------------

# 15. AI Coding Agent Rules

Agents must:

1.  Treat replay as a first-class acquisition source.
2.  Never require physical hardware for algorithm testing.
3.  Ensure new reconstruction features support replay validation.
4.  Keep simulation output compatible with real DAQ format.
5.  Preserve dataset provenance.
6.  Never modify archived raw data.
7.  Add regression tests using reference datasets.

------------------------------------------------------------------------

# 16. Final Decision

The acquisition architecture shall support:

                     Acquisition Service


            +------------+-------------+

            |            |             |

          Real        Replay       Simulation

          DAQ         Data          Data


            +------------+-------------+

                         |

                  Unified Raw Stream

                         |

                 Reconstruction Engine

                         |

                     Muon EDM

                         |

                  Digital Twin / Apps

The replay service is a core platform capability, not a testing utility.

It is the bridge between prototype instruments, software development, AI
training, and future commercial deployments.
