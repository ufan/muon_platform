# Architecture Decision Report (ADR-07)

Status: reference. Original option study (2026) behind [ADR-007](../adr/ADR-007_digital_twin_strategy.md); the ADR holds the decision, and later decisions override this text. Its agent-rule and repository-layout sections are obsolete.

# Muography Instrument Product Architecture and Digital Twin Strategy

Version: 1.0

# 1. Decision Summary

This document defines the product-level architecture connecting the
physical muography instrument, scientific reconstruction pipeline,
engineering models, and digital twin applications.

Decision:

-   Treat the instrument as a complete sensing platform, not only a
    detector.
-   Separate measurement data, reconstruction results, engineering
    models, and user applications.
-   Use digital twin technology as the integration layer between
    scientific results and engineering decisions.
-   Maintain consistency between simulation models, deployment geometry,
    reconstruction geometry, and visualization assets.

------------------------------------------------------------------------

# 2. Motivation

A commercial muography instrument provides value through the complete
chain:

    Physical World

        |

    Muon Measurement

        |

    Scientific Reconstruction

        |

    Engineering Interpretation

        |

    Decision Support

The detector hardware is only one component.

The long-term product value comes from:

-   reconstruction algorithms
-   application-specific models
-   accumulated measurement data
-   engineering workflows
-   AI interpretation

------------------------------------------------------------------------

# 3. Digital Twin Concept

The digital twin is not simply a 3D visualization.

It is the synchronized representation of:

    Physical Object

    +

    Measurement System

    +

    Scientific Data

    +

    Engineering Interpretation

For muography applications:

    Dam / Tunnel / Industrial Object

              |

    Geometry Model

              |

    Muon Detector Deployment Model

              |

    Measured Data

              |

    Density Reconstruction

              |

    Engineering Assessment

------------------------------------------------------------------------

# 4. Digital Twin Layers

## Layer 1: Physical Object Model

Represents the inspected object.

Examples:

-   dam geometry
-   tunnel structure
-   TBM environment
-   industrial furnace

Sources:

-   CAD
-   BIM
-   survey data
-   geological models

Possible tools:

-   FreeCAD
-   OpenSCAD
-   Blender
-   IFC/BIM tools

------------------------------------------------------------------------

## Layer 2: Detector Deployment Model

Represents the measurement system.

Contains:

-   detector position
-   orientation
-   field of view
-   acceptance
-   calibration

Example:

    Detector Pose

    +

    Angular Acceptance

    +

    Geometry

------------------------------------------------------------------------

## Layer 3: Measurement Data Model

Contains:

-   raw detector data
-   reconstructed tracks
-   angular distributions
-   environmental conditions

Based on:

-   Muon EDM
-   raw archive
-   reconstructed data products

------------------------------------------------------------------------

## Layer 4: Density Field Model

Scientific reconstruction output.

Examples:

-   opacity map
-   density voxel field
-   anomaly probability

Represented as:

    3D Grid

    +

    Density Value

    +

    Uncertainty

    +

    Timestamp

------------------------------------------------------------------------

## Layer 5: Engineering Interpretation

Transforms physics results into engineering information.

Examples:

Dam:

    Density anomaly

            |

    Possible seepage region

            |

    Risk indicator

TBM:

    Density anomaly

            |

    Possible cavity

            |

    Advance warning

------------------------------------------------------------------------

# 5. Data Flow Architecture

                     Applications


            Digital Twin Platform

            Visualization

            Engineering Analysis


                        |

                 Data Products


                        |

              Reconstruction Platform


                        |

                  Muon EDM


                        |

              Detector Measurement


                        |

                  Physical Object

------------------------------------------------------------------------

# 6. Relationship Between Simulation and Operation

The same model should support:

## Simulation

    Geometry Model

          |

    Synthetic Density Field

          |

    Muon Simulation

          |

    Synthetic Detector Data

------------------------------------------------------------------------

## Operation

    Real Geometry

          |

    Measured Data

          |

    Reconstruction

          |

    Updated Density Model

This creates a closed engineering loop.

------------------------------------------------------------------------

# 7. Recommended Technical Stack

## Geometry

Possible:

-   FreeCAD
-   OpenSCAD
-   Blender
-   CAD/BIM import

------------------------------------------------------------------------

## Scientific Visualization

Recommended:

-   VTK
-   ParaView

Capabilities:

-   detector placement
-   muon tracks
-   density volume rendering
-   anomaly visualization

------------------------------------------------------------------------

## Data Processing

Core:

-   Muon EDM
-   Taskflow reconstruction
-   Arrow/Parquet data products

------------------------------------------------------------------------

## Application Layer

Possible:

-   Qt/QML desktop application
-   Web visualization
-   Cloud dashboard

------------------------------------------------------------------------

# 8. Example: Dam Monitoring Workflow

    Dam CAD Model

           |

    Detector Deployment

           |

    Muon Acquisition

           |

    Track Reconstruction

           |

    Density Inversion

           |

    3D Density Field

           |

    Digital Twin Update

           |

    Engineering Evaluation

------------------------------------------------------------------------

# 9. Example: TBM Advance Prediction Workflow

    TBM Position

           |

    Detector Pose

           |

    Muon Transmission Data

           |

    Forward Density Reconstruction

           |

    Geological Risk Map

           |

    TBM Decision Support

------------------------------------------------------------------------

# 10. Product Architecture

The overall platform becomes:

                      User Applications

              Digital Twin / Cloud / GUI


                             |

                      Data Products


                             |

                 Scientific Computing Layer


            Reconstruction

            Density Inversion

            AI Interpretation


                             |

                     Instrument Platform


            DAQ

            HV

            Gas

            Pose


                             |

                     Detector Hardware

------------------------------------------------------------------------

# 11. Design Principles

## Principle 1

The geometry model is a first-class object.

It must be shared by:

-   simulation
-   reconstruction
-   visualization

------------------------------------------------------------------------

## Principle 2

Scientific results must retain provenance.

Every result should know:

    geometry_version

    detector_version

    calibration_version

    algorithm_version

    timestamp

------------------------------------------------------------------------

## Principle 3

Visualization is not an afterthought.

The same data products should support:

-   debugging
-   scientific analysis
-   customer reporting
-   digital twin applications

------------------------------------------------------------------------

# 12. AI Coding Agent Rules

Agents working on digital twin features should:

1.  Keep geometry models separated from visualization code.
2.  Use shared schemas for detector and object models.
3.  Preserve data provenance.
4.  Avoid hard-coded geometry.
5.  Keep simulation and operation models consistent.
6.  Treat visualization outputs as data products, not temporary
    graphics.

------------------------------------------------------------------------

# 13. Roadmap

## Phase 1

Build:

-   detector geometry model
-   simple 3D visualization
-   reconstructed track display

------------------------------------------------------------------------

## Phase 2

Add:

-   density field visualization
-   anomaly marking
-   engineering annotations

------------------------------------------------------------------------

## Phase 3

Add:

-   cloud digital twin
-   multi-instrument management
-   AI-assisted interpretation

------------------------------------------------------------------------

# 14. Final Decision

The muography instrument platform shall be developed as:

    Measurement Device

            +

    Scientific Reconstruction System

            +

    Digital Twin Platform

            +

    Engineering Application Layer

The digital twin is the bridge between advanced detector technology and
practical industrial value.
