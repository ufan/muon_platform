# ADR-007 Digital twin

Status: Accepted (re-baselined 2026-10-25). Option study: [digital twin report](../design/digital_twin_report.md).

## Decision

- The product is a complete sensing platform; its value runs from measurement through
  reconstruction to engineering interpretation.
- Measurement data, reconstruction results, engineering models and applications are separate layers.
- The digital twin links the physical object model, detector deployment, measurement products,
  density field and engineering interpretation.
- Geometry is independent of visualization code, and model identities are the same across
  simulation, reconstruction and display.

## Why

Users act on interpreted density in the context of their structure, not on detector data.

## Consequences

- Geometry sources (CAD/BIM, surveys, geological models) and tools (FreeCAD, Blender, VTK,
  ParaView) are options, not runtime dependencies, until an application iteration chooses them.
