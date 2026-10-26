# ADR-008 Data sources and verification

Status: Accepted (re-baselined 2026-10-25; revised and confirmed by owner 2026-10-26: physics simulation removed)

## Decision

- Recorded raw data is an immutable engineering asset, archived and versioned. Curated recordings
  are the offline datasets (`testdata`, [ADR-011](ADR-011_test_data.md)).
- **Offline data** is for iterating and verifying single features and components (decoding, hit
  building, tracking, …): they run directly on versioned datasets, without the online pipeline.
- **Live and replay** are equivalent sources behind one raw-stream contract; downstream processing
  does not know the source. Replay mainly verifies the online pipeline end to end (pacing,
  ordering, backpressure, event building) without hardware.
- Physics simulation (detector Monte Carlo such as Geant4) is not part of this project; offline
  and replayed data drive reconstruction algorithm development.
- Hardware domain simulators and fakes stay ([ADR-003](ADR-003_hardware_domains_services_and_controllers.md)); they are the
  integration-test infrastructure for domain services and the instrument.
- Verification layers: unit and contract tests, offline-dataset regression against golden data,
  online-pipeline replay, domain-simulator integration tests and hardware-in-the-loop tests.

## Why

Hardware is scarce and slow to test with; recorded data gives fast, reproducible development,
regression testing and demonstrations. Offline datasets keep component iterations small and fast;
replay exercises the online pipeline as a whole. Physics simulation adds little to rapid prototyping of most
components, and offline and replayed data already support the reconstruction algorithm iterations.

## Alternatives

- Geant4 plus fast detector response inside the platform, as a third acquisition source with
  synthetic truth: removed 2026-10-26 for the reasons above. Physics simulation may become a
  separate project; it would feed this pipeline only through the raw-stream contract.

## Consequences

- Source policies (pacing, clock, backpressure, sinks) are the only mode differences
  ([acquisition sources](../../../core/daq/doc/specs/acquisition-sources.md)).
- Golden datasets follow [ADR-011](ADR-011_test_data.md).
