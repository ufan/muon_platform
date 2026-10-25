# ADR-002 Muon EDM and serialization

Status: Accepted (re-baselined 2026-10-25)

## Decision

- The Muon Event Data Model (EDM) is the scientific contract between algorithms: events, raw hits,
  hits, clusters, tracks and conditions.
- Algorithms never depend on binary or file formats; serialization stays outside algorithm code.
- Layers: raw binary (immutable) → EDM → data products → analytics storage.
- Candidate formats: protobuf for service messages, Arrow/Parquet for analytics. The raw-capture
  container is decided separately (DAQ iteration).
- Every result records its provenance (system architecture §6).

## Why

A stable in-memory model lets algorithms, formats and storage evolve independently and keeps
results reproducible.

## Consequences

- EDM schemas live in `core/contracts/science/` and change with their consumers.
