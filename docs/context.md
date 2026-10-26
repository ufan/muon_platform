# Agent primer

Status: current (short primer for agents; every fact here has an owning document it links to).

Read this before design or architecture work, and when a task touches boundaries, contracts, data
or deployment. For small edits, read only the documents relevant to the change.

## Product

A portable muography instrument: Micromegas detectors track cosmic-ray muons, and the angular muon
flux behind a large object reveals its density. Applications include TBM advance geological
prediction, dam and infrastructure monitoring, industrial inspection and geological exploration.
The value lies beyond the detector: reliable operation, stable data contracts, reconstruction
quality, accumulated datasets and application products.
More: [product and system requirements](requirements/system_requirements.md).

## Where to look

| Question | Document |
|---|---|
| What the product must do; applications, deployment modes | [requirements/system_requirements.md](requirements/system_requirements.md) |
| How the system is built: domains, planes, data path, conditions | [architecture/system_architecture.md](architecture/system_architecture.md) |
| Scientific chain: modules, stages, contracts, downstream needs | [architecture/architecture_overview.md](architecture/architecture_overview.md) |
| Repositories and dependency rules | [architecture/repository_model.md](architecture/repository_model.md) |
| Why a decision was made | [adr/README.md](adr/README.md) |
| How the project is developed: specs, changes, rigor, legacy | [workflow/engineering_process.md](workflow/engineering_process.md) |
| Proposals and research (not decisions) | [design notes](README.md#design-notes) |
| A component's behaviour | its `SPEC.md` |

Authority comes from each document's declared status and scope and from explicit supersession, not
from specificity or ADR number ([docs index](README.md)). Flag conflicts instead of choosing silently.

## Invariants

Never break these without an ADR:

- Hardware stays behind domain services; applications and orchestration never address devices
  ([ADR-003](adr/ADR-003_hardware_domains_services_and_controllers.md)). DAQ has its own data link.
- Algorithms exchange Muon EDM objects in an in-process DAG and read only immutable conditions,
  never live telemetry, files or config ([ADR-001](adr/ADR-001_reconstruction_runtime.md),
  [ADR-002](adr/ADR-002_muon_edm_serialization.md)).
- Online and offline share the same code; live and replay share one raw-stream contract
  ([ADR-008](adr/ADR-008_data_sources_and_verification.md)).
- Raw data is immutable, and every scientific product is traceable to its inputs and versions.
- Dependencies point one way; core never commands another domain
  ([ADR-015](adr/ADR-015_repository_and_instrument_layering.md)).
- Linux ARM64 stays supported; add dependencies only for a real need.
- Update the owning document when a boundary, contract, deployment assumption or validation
  strategy changes.
