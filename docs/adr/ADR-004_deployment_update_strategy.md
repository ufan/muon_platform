# Architecture Decision Report (ADR)

# Muon Instrument Deployment and Update Strategy

Version: 1.0

## 1. Decision Summary

This document defines the deployment, lifecycle management, update, and
versioning strategy for the muography instrument software platform.

The objective is to transform the software architecture from a
laboratory prototype into a maintainable commercial scientific
instrument platform.

The selected approach:

-   Linux ARM64 edge appliance as the deployment target.
-   systemd-based service lifecycle management.
-   Package-based software deployment initially.
-   Atomic OTA update capability reserved for production scale.
-   Unified version model covering hardware, firmware, software,
    algorithms, and calibration.
-   CI/CD supporting x86_64 development and ARM64 deployment.
-   Configuration and calibration separated from executable software.

------------------------------------------------------------------------

# 2. Design Goals

The deployment system must support:

-   long instrument lifetime (5-10 years)
-   remote maintenance
-   multiple product variants
-   reproducible software builds
-   safe updates in field environments
-   offline deployment when network is unavailable
-   AI-assisted development workflow

------------------------------------------------------------------------

# 3. Deployment Architecture

                     Development Platform

            Git Repository

                  |

            CI/CD Pipeline

                  |

        +-----------------------+

        | Build Artifacts       |

        |                       |

        | x86_64 packages       |

        | ARM64 packages        |

        | Firmware binaries     |

        +-----------------------+

                  |

           Artifact Repository

                  |

           Deployment Package


    ================================================

                  Instrument Edge Device

    ================================================


                  Device Manager


           +-----------------------------+

           |                             |

     Linux Services                Firmware

     DAQ Service                  FPGA

     HV Service                   STM32

     Gas Service

     Reconstruction


           |

     Configuration Manager


           |

     Calibration Database

------------------------------------------------------------------------

# 4. Software Packaging Decision

## Option A: Debian packages

Selected for initial production.

Advantages:

-   native Linux ecosystem
-   simple dependency management
-   easy rollback
-   transparent debugging

Example:

    muon-daq_1.2.0_arm64.deb

    muon-reco_0.8.0_arm64.deb

    muon-services_1.0.0_arm64.deb

------------------------------------------------------------------------

## Option B: Containers

Possible future option.

Advantages:

-   reproducible environment
-   easy deployment

Disadvantages:

-   additional runtime complexity
-   resource overhead
-   less natural for hardware access

Decision:

Use selectively for cloud/server components, not core hardware services.

------------------------------------------------------------------------

## Option C: AppImage/custom bundle

Rejected.

Reasons:

-   weaker dependency management
-   less suitable for long-lived products

------------------------------------------------------------------------

# 5. Service Lifecycle Management

## Selected approach

Use Linux systemd.

Example:

    muon-daq.service

    muon-hv.service

    muon-gas.service

    muon-reco.service

    muon-health.service

Advantages:

-   built into Linux
-   robust restart mechanism
-   logging integration
-   simple operation model

------------------------------------------------------------------------

# 6. OTA Update Strategy

## Production requirements

The update system should support:

-   atomic update
-   rollback
-   version verification
-   remote deployment
-   offline recovery

Candidate technologies:

## RAUC

Strengths:

-   embedded Linux oriented
-   A/B update
-   secure deployment

## Mender

Strengths:

-   fleet management
-   enterprise features

## SWUpdate

Strengths:

-   lightweight embedded solution

Decision:

Prototype:

    Deb package update

    +

    systemd restart

Production:

Evaluate:

    RAUC

    or

    Mender

------------------------------------------------------------------------

# 7. Version Model

Every instrument state must be reproducible.

The instrument version is:

    Instrument Release

    =

    Hardware Version

    +

    Firmware Version

    +

    Software Version

    +

    Algorithm Version

    +

    Calibration Version

    +

    Configuration Version

Example:

``` yaml
instrument:
  model: MUON400

hardware:
  detector: micromegas_v3
  hv_board: hvb_v2

firmware:
  fpga: 1.4.2
  stm32: 2.1.0

software:
  reco: 0.8.5
  services: 1.1.0

algorithm:
  tracker: kalman_v3

calibration:
  gain_map: 2026_07_01

configuration:
  deployment: tbm_mode
```

------------------------------------------------------------------------

# 8. Configuration Management

Configuration must not be compiled into software.

Separate:

    Executable

    +

    Configuration

    +

    Calibration

    +

    Geometry

Examples:

    detector.yaml

    hv.yaml

    gas.yaml

    geometry.yaml

    pipeline.yaml

Benefits:

-   easier customer customization
-   reproducibility
-   safer updates

------------------------------------------------------------------------

# 9. Calibration Management

Calibration data is scientific data.

It must be versioned independently.

Examples:

    gain_map

    alignment

    efficiency_map

    noise_map

    temperature_correction

Each reconstruction result should reference:

    calibration_id
    geometry_id
    algorithm_version

------------------------------------------------------------------------

# 10. Product Variant Strategy

Avoid creating separate software forks.

Example products:

    MUON400-TBM

    MUON400-DAM

    MUON400-LAB

Share:

    Muon EDM

    Reconstruction

    Services

    Deployment system

Customize:

    hardware driver

    geometry

    configuration

    calibration

    pipeline

------------------------------------------------------------------------

# 11. CI/CD Architecture

Recommended:

    Developer

       |

    Git

       |

    CI Pipeline

       |

    +----------------+

    Build x86_64

    Build ARM64

    Unit Tests

    Simulation Tests

    Hardware Tests

    +----------------+

       |

    Artifact Repository

------------------------------------------------------------------------

# 12. AI Coding Agent Rules

> Historical rule list. Current agent rules: `platform/AGENTS.md` and [engineering context](../engineering_context.md). Rule 3 is not in force as a per-change gate: the current gate is `muon verify` per repository (ADR-012 §6), while ARM64 support remains a design constraint.

AI agents must follow:

1.  Never modify hardware-specific code outside service boundaries.
2.  Every software component must have explicit ownership.
3.  Every change must pass x86_64 and ARM64 builds.
4.  Configuration changes must not modify source code.
5.  Calibration data must never be embedded in binaries.
6.  New features must preserve backward compatibility of EDM.
7.  Firmware/software versions must be traceable.
8.  Production deployment requires reproducible artifacts.

------------------------------------------------------------------------

# 13. Recommended Technology Stack

## Development

-   Git
-   CMake
-   Conan/vcpkg
-   GitHub Actions/GitLab CI

## Build

-   GCC/Clang
-   cross compilation toolchain
-   ARM64 CI target

## Runtime

-   Linux ARM64
-   systemd
-   Debian packages

## Update

Prototype:

-   package update

Production:

-   RAUC/Mender/SWUpdate evaluation

------------------------------------------------------------------------

# 14. Final Architecture

                    Cloud Platform

              Fleet Management

              Data Storage

              Monitoring


                        |

                  OTA / API


                        |

    ================================================

                 Muon Instrument Edge

    ================================================


              Device Management Layer


                  systemd


                        |

          +-------------+-------------+

          |                           |

     Software Services          Firmware

     DAQ                         FPGA

     HV                          STM32

     Gas

     Pose

     Reconstruction


                        |

              Configuration + Calibration


                        |

                     Hardware

------------------------------------------------------------------------

# 15. Final Decision

The platform should evolve as:

Prototype:

    Linux ARM64

    +

    systemd services

    +

    Deb packages

    +

    Git CI/CD

Production:

    Linux ARM64

    +

    systemd

    +

    RAUC/Mender

    +

    fleet management

    +

    versioned calibration/configuration

This architecture minimizes operational burden while preserving a path
to industrial-scale deployment.
