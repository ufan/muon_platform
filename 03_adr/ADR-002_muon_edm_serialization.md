# ADR-002 Muon EDM and Serialization Architecture

## Decision

Create a stable Muon Event Data Model as the scientific contract.

Algorithms must not depend on binary formats.

## Data Layers

Raw Binary

|

Muon EDM

|

Data Products

|

Analytics Storage

## Core Objects

- MuonEvent
- Hit
- Cluster
- Track
- Conditions

## Serialization Strategy

Evaluate:

- protobuf for service communication
- Arrow/Parquet for analytics storage

Scientific provenance is mandatory.

Every result records:

- instrument version
- geometry version
- calibration version
- algorithm version
- timestamp
