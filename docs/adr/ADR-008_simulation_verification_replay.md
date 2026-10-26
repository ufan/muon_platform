# ADR-008 Simulation, replay and verification

Status: Accepted (re-baselined 2026-10-25)

## Decision

- Live acquisition, recorded replay and simulation are equivalent sources behind one raw-stream
  contract. Downstream processing does not know the source.
- Recorded raw data is an immutable engineering asset, archived and versioned.
- Simulation (Geant4 plus fast detector response) outputs the real acquisition format with
  synthetic truth.
- Verification layers: unit and contract tests, dataset regression against golden data, simulation
  validation and hardware-in-the-loop tests.

## Why

Hardware is scarce and slow to test with; replay and simulation give fast, reproducible
development, regression testing, demonstrations and training data.

## Consequences

- Source policies (pacing, clock, backpressure, sinks) are the only mode differences
  ([acquisition sources](../../../core/daq/doc/specs/acquisition-sources.md)).
- Golden datasets follow [ADR-011](ADR-011_test_data.md).
