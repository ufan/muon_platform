# Architecture Decision Report (ADR-05)

# Hardware Abstraction and Domain Controller Interface Architecture

Version: 1.0

## 1. Decision Summary

The muography instrument hardware architecture shall use independent
domain controllers with stable software interfaces.

Domain controllers:

-   Gas subsystem controller
-   High-voltage subsystem controller
-   Pose/motion controller
-   DAQ controller

The central ARM64 controller shall not directly control low-level
hardware.

Decision:

-   Deterministic functions stay inside domain controllers.
-   Central controller performs orchestration, fusion, reconstruction,
    and external communication.
-   Service interfaces are defined independently from hardware
    implementation.

------------------------------------------------------------------------

# 2. Design Principle

The architecture follows:

    Hardware Domain

            |

    Firmware Controller

            |

    Service Interface

            |

    Central Instrument Software

The service contract is the boundary.

------------------------------------------------------------------------

# 3. Domain Controller Responsibilities

## Gas Controller

Responsibilities:

-   valve control
-   flow regulation
-   pressure monitoring
-   safety interlocks

Interface examples:

    SetFlow()

    GetPressure()

    GetTemperature()

    GetStatus()

------------------------------------------------------------------------

## HV Controller

Responsibilities:

-   voltage ramping
-   current monitoring
-   fault protection
-   discharge handling

Interface examples:

    SetVoltage()

    GetVoltage()

    GetCurrent()

    EnableOutput()

    ClearFault()

------------------------------------------------------------------------

## Pose Controller

Responsibilities:

-   IMU processing
-   position estimation
-   motor control (future)

Interface:

    GetPose()

    SetMotion()

    GetStatus()

------------------------------------------------------------------------

## DAQ Controller

Responsibilities:

-   FPGA communication
-   event acquisition
-   timestamp generation
-   high-rate streaming

Interface:

    StartRun()

    StopRun()

    ReadEvent()

    GetStatus()

------------------------------------------------------------------------

# 4. Communication Interface Decision

Recommended hierarchy:

    High-level service

            |

    gRPC / protobuf

            |

    Domain adapter

            |

    CAN-FD / RS485 / Ethernet / USB

            |

    Hardware

------------------------------------------------------------------------

# 5. Modbus RTU Evaluation

Suitable for:

-   industrial sensors
-   simple configuration
-   slow control

Not suitable as the universal instrument bus.

Limitations:

-   low bandwidth
-   weak type system
-   poor event streaming

Use for:

-   gas subsystem
-   auxiliary sensors

------------------------------------------------------------------------

# 6. CAN-FD Evaluation

Advantages:

-   deterministic
-   robust
-   automotive proven
-   good embedded support

Suitable for:

-   distributed controllers
-   safety critical control

Limitations:

-   limited payload
-   not suitable for DAQ streams

------------------------------------------------------------------------

# 7. Ethernet Evaluation

Recommended for:

-   DAQ
-   high-rate data
-   future expansion

Technologies:

-   TCP
-   UDP
-   gRPC
-   Zenoh

------------------------------------------------------------------------

# 8. Firmware Architecture

Recommended:

STM32 + Zephyr RTOS

Structure:

    Drivers

     |

    Hardware Abstraction

     |

    Control Logic

     |

    Communication Service

Firmware should expose capabilities, not registers.

------------------------------------------------------------------------

# 9. Final Architecture

                    ARM64 Central Controller


                 Instrument Service Layer


            Gas Service
            HV Service
            Pose Service
            DAQ Service


                 |

           Domain Communication


                 |

            STM32 / FPGA Controllers


                 |

              Hardware

------------------------------------------------------------------------

# 10. AI Coding Agent Rules

-   Never access hardware registers from application layer.
-   Keep hardware drivers isolated.
-   Define APIs before implementation.
-   Treat domain controllers as independent products.
-   Maintain simulation backends for every hardware service.
