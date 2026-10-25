# Muography Instrument Product Landscape

Status: reference. Product vision and use-case narrative. Requirements: [SRD](../requirements/SRD.md); architecture: [system architecture](../architecture/system_architecture.md); its architecture and hardware sections (§9–§12) are superseded by them.

# 1. Purpose

This document provides the top-level landscape view of the planned
muography instrument platform.

It defines:

-   the mission of the instrument
-   major application domains
-   typical deployment scenarios
-   system composition
-   relationship between hardware, software, reconstruction, and cloud
    services

This document serves as the context layer above detailed architecture
decisions.

------------------------------------------------------------------------

# 2. Instrument Vision

The planned muography instrument is a portable scientific sensing
platform based on Micromegas gaseous detectors.

Its purpose is:

> Non-invasive density imaging and structural monitoring of large-scale
> objects by measuring natural cosmic-ray muon transmission.

Unlike conventional inspection methods, the instrument provides:

-   passive measurement
-   large-volume penetration
-   long-term monitoring capability
-   three-dimensional density reconstruction

------------------------------------------------------------------------

# 3. Core Technology Concept

Natural cosmic-ray muons continuously penetrate the Earth.

When passing through matter:

-   high-density regions absorb more muons
-   low-density regions allow more transmission

The instrument measures:

    Incoming muon

          |

    Detector telescope

          |

    Muon trajectory reconstruction

          |

    Angular flux measurement

          |

    Density inversion

          |

    3D density information

------------------------------------------------------------------------

# 4. Target Application Domains

The platform targets large-scale infrastructure and industrial scenarios
where traditional inspection methods are difficult.

Main domains:

1.  Underground engineering
2.  Civil infrastructure health monitoring
3.  Industrial process monitoring
4.  Geological exploration
5.  Research and scientific applications

------------------------------------------------------------------------

# 5. Primary Use Case: TBM Advance Geological Prediction

## Scenario

Tunnel boring machines operate underground where direct geological
observation is difficult.

Challenges:

-   unknown geology ahead of cutter head
-   hidden cavities
-   water-bearing zones
-   abnormal geological structures

------------------------------------------------------------------------

## Deployment

    Tunnel

            TBM

            |

            Detector

            |

            Forward looking volume

------------------------------------------------------------------------

## Muography Value

Provides:

-   ahead-of-face density variation
-   cavity detection
-   geological anomaly indication

Data products:

-   density anomaly map
-   risk indicator
-   geological prediction report

------------------------------------------------------------------------

# 6. Civil Infrastructure: Dam Health Monitoring

## Scenario

Large dams require lifetime structural monitoring.

Important concerns:

-   seepage
-   internal erosion
-   density degradation
-   hidden voids
-   foundation anomalies

------------------------------------------------------------------------

## Deployment

    Detector

          |

          |

           Dam body

          |

    Density reconstruction

------------------------------------------------------------------------

## Muography Value

Advantages:

-   non-invasive
-   large volume observation
-   long-term monitoring

Outputs:

-   density distribution
-   anomaly evolution
-   digital twin update

------------------------------------------------------------------------

# 7. Industrial Applications

## 7.1 Blast Furnace / Large Industrial Equipment

Challenges:

-   inaccessible interior
-   high temperature
-   large structures

Possible targets:

-   burden distribution
-   material density
-   internal wear

------------------------------------------------------------------------

## 7.2 Large Storage Structures

Examples:

-   tanks
-   silos
-   reactors

Potential monitoring:

-   filling distribution
-   density changes
-   abnormal regions

------------------------------------------------------------------------

# 8. Instrument Deployment Modes

## Mode A: Survey Instrument

Purpose:

Short-term investigation.

Characteristics:

-   mobile deployment (multi-sites or single-site)
-   optimized geometry
-   offline reconstruction

Workflow:

    Deploy

     |

    Acquire data

     |

    Reconstruct

     |

    Engineering evaluation

------------------------------------------------------------------------

## Mode B: Continuous Monitoring Instrument

Purpose:

Structural health monitoring.

Characteristics:

-   fixed installation (multi-sites or single-site)
-   quasi-realtime report with a moving time window
-   continuous acquisition
-   cloud connection

Workflow:

    Instrument

     |

    Streaming data

     |

    Online reconstruction

     |

    Trend analysis

     |

    Warning

------------------------------------------------------------------------

# 9. Instrument System Architecture Overview

                        User Applications

            Visualization / Cloud / Digital Twin


                             |

                     Data Products


                             |

                  Reconstruction Platform


                             |

            Hardware Control + Data Acquisition


                             |

                  Detector Electronics


                             |

                    Micromegas Detector

------------------------------------------------------------------------

# 10. Hardware Platform Composition

The instrument consists of several independent domains.

## Detector DAQ Domain

Function:

-   detector readout
-   FPGA processing
-   event generation

------------------------------------------------------------------------

## High Voltage Domain

Function:

-   detector bias generation
-   current monitoring
-   protection

------------------------------------------------------------------------

## Gas System Domain

Function:

-   flow regulation
-   valve on/off
-   periodic gas path on/off mimicing micro-flow
-   optional pressure monitoring

------------------------------------------------------------------------

## Position and Motion Domain

Function:

-   instrument pose
-   orientation
-   global position
-   future scanning motion control

------------------------------------------------------------------------

## Environmetal Sensing Domain

Function:
-   Internal and External temperature and humdity
-   Vibration frequency
-   Atomsphere pressure

## Central Computing Domain

Function:

-   data fusion
-   reconstruction
-   communication: device control, status reporting, data products streaming
-   user interface: headless backend with remote web access and local debug port, optionally local GUI display

------------------------------------------------------------------------

# 11. Software Platform Overview

## Data-plane
    Data Service and Applicaiton

          |

    Data Products Layer

          |

    Reconstruction Engine

          |

    Muon EDM

## Control-plane
    Instrument Service and Application

    Domain Aggregation Layer
          |

    Domain Services

          |

    Hardware Abstraction Layer

------------------------------------------------------------------------

# 12. Scientific Data Flow

    Detector Raw Data

            |

    Binary Decoding

            |

    Hit Reconstruction

            |

    Cluster Reconstruction

            |

    Track Reconstruction

            |

    Angular Distribution

            |

    Density Inversion

            |

    Engineering Information

------------------------------------------------------------------------

# 13. Product Evolution Roadmap

## Generation 1

Focus:

-   reliable detector operation
-   manual deployment
-   offline reconstruction

## Generation 2

Focus:

-   online reconstruction
-   remote monitoring
-   automated diagnostics

## Generation 3

Focus:

-   multi-instrument deployment
-   cloud analytics
-   AI-assisted interpretation

------------------------------------------------------------------------

# 14. Strategic Positioning

The product is not only a detector.

It is a complete sensing system:

    Detector Hardware

    +

    Embedded Control

    +

    Scientific Reconstruction

    +

    Data Platform

    +

    AI Interpretation

The long-term value is created by:

-   proprietary reconstruction algorithms
-   application-specific models
-   accumulated measurement data
-   engineering workflows

------------------------------------------------------------------------