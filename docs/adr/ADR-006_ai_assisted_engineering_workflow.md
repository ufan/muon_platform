# Architecture Decision Report (ADR-06)

# AI-Assisted Engineering Workflow for Muography Instrument Platform

Version: 1.0

## 1. Decision Summary

AI coding agents shall be integrated as engineering assistants operating
under explicit architecture constraints.

The goal:

-   increase solo developer productivity
-   preserve architecture consistency
-   reduce integration mistakes

------------------------------------------------------------------------

# 2. Repository Organization

> **Superseded by [ADR-009](ADR-009_workspace_repository_model.md)** (2026-10-21) and
> [ADR-012](ADR-012_repository_baseline_and_workflow.md) (2026-10-23). The monorepo layout below is kept
> for history only. The platform uses one repository per domain, composed with vcs2l and the `muon` tool.

Recommended structure:

    muon-platform/

     hardware/

       hv_controller/

       gas_controller/

       pose_controller/

       daq_controller/


     firmware/

       stm32/


     software/

       services/

       reconstruction/

       muon_edm/


     tools/

     simulation/

     deployment/

     docs/

------------------------------------------------------------------------

# 3. Architecture Documentation as Agent Context

Maintain:

    AGENTS.md

    ARCHITECTURE.md

    ADR/

    interfaces/

AI agents must read:

-   architecture decisions
-   API definitions
-   coding rules

before modifying code.

------------------------------------------------------------------------

# 4. Specification Driven Development

> Detailed by [ADR-010](ADR-010_spec_driven_domain_iteration.md): spec
> layers, change proposals, and the per-domain iteration playbook.

Before implementation:

    Requirement

        |

    Interface Definition

        |

    Test Case

        |

    Implementation

Examples:

protobuf:

    HVService.proto

EDM:

    MuonEvent.schema

Hardware:

    register_map.yaml

------------------------------------------------------------------------

# 5. Build System

Recommended:

    CMake

    +

    Conan/vcpkg

    +

    CI

Targets:

    Linux x86_64

    Linux ARM64

    STM32 firmware

------------------------------------------------------------------------

# 6. AI Agent Development Loop

Recommended workflow:

    Human defines architecture

            |

    AI generates implementation

            |

    CI validates

            |

    Hardware/simulation test

            |

    Human review

AI should not make architectural decisions automatically.

------------------------------------------------------------------------

# 7. Testing Strategy

Layers:

## Unit Test

Algorithms:

-   decoder
-   hit reconstruction
-   tracker

## Simulation Test

Synthetic detector data:

    Monte Carlo

        |

    DAQ format

        |

    Reconstruction

## Hardware-in-loop Test

Real:

-   FPGA
-   HV
-   sensors

------------------------------------------------------------------------

# 8. Simulation First

Every hardware service should have:

    Real Backend

          |

    Common API

          |

    Simulation Backend

Example:

    HVService

        |
        +-- STM32 backend

        |
        +-- simulator backend

------------------------------------------------------------------------

# 9. AI Coding Rules

> Historical rule list. Current agent rules: `platform/AGENTS.md` and [engineering context](../engineering_context.md).

Agents must:

1.  Respect ADR documents.
2.  Never bypass interfaces.
3.  Add tests with features.
4.  Avoid unnecessary dependencies.
5.  Keep ARM64 compatibility.
6.  Prefer existing libraries.
7.  Update documentation with architecture changes.

------------------------------------------------------------------------

# 10. Final Engineering Model

The company operates like a virtual engineering team:

    Architecture Owner

            |

    AI Coding Agents

            |

    CI/CD

            |

    Simulation

            |

    Hardware Validation

            |

    Product Release

The architecture documents are the long-term memory of the engineering
system.
