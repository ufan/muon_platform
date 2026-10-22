# ADR-001 Reconstruction Runtime Architecture

## Decision

Use an internal DAG-based reconstruction runtime.

Initial technology:

- Taskflow

The reconstruction pipeline is not implemented as microservices.

## Rationale

Physics reconstruction requires:

- low latency
- shared memory
- deterministic execution
- algorithm iteration

## Architecture

Raw Event

|

Taskflow DAG

|

Decoder

|

Hit Reconstruction

|

Cluster Reconstruction

|

Track Reconstruction

|

Physics Products

## Rules

Algorithms communicate only through Muon EDM.

Algorithms must support replay datasets.
