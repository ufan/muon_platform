# overview

Status: historical (original project brief and brainstorming, 2026-10). Superseded by the [product landscape](../product_landscape.md), [repository model](../architecture/repository_model.md) and [ADR-012](../adr/ADR-012_repository_baseline_and_workflow.md); West adoption and the repository list below are not current.

I am building a new hardware and software system used for muography. We have already MVP of the hardware system, and some PoC level software code and algorithms. I wanna redesign the new system top-down: refactor our existing codebases, add missing components, and integrate them into one consistent platform with robustness, modularity and extensiblity in mind. Right now in my mind, the platform/system needs to have the following modules:
- daq: retrieval raw data from our detector system and a robust device state machine
- protocol: wire-line protocol schema, pipeline and persistence object schema, and optionally database schema
- config: all kinds of configuration files, channel mapping files, calibration and detector definition
- simulation: Geant4 based simulation toolkits for evaluation case study
- preprocess: raw binary unpack, decode and data filtering
- reconstruction: detector hits and muon track find and fit
- analysis: for detctor data analysis, muon flux calcualtion
- calibration: efficiency, flux, detector response
- imaging: 2d and 3d imaging algorithms commonly used in mungraphy
- ux: tui, gui, web ui and visualization layer
- tools
- applications

Based on the usage, the components of the platform may be deployed in a headless device SoC (in DAQ case) or a high-grade server (in imaging case); in a production ready environment (like industry field) or in test environment (like testbench in the lab).

the daq acts as interface to the underlying data acquisition hardware. but, the detector system is much more complicated and
  is a much bigger system consists of the following subsystems: 1) daq acquisition; 2) sensor network: humidity, temparature,
  vibration, Inclinometer etc.; 3) gas control: mass flow controller, solenoid valve, pressure gauge, plc; 4) cooling and
  dehumidifier; 5) voltage supply: high voltage module for detectors and low voltage for all other components. Most of other
  subsystems use modbus protocol underneath, grouped into three RS485 bus. In real world use case, it's very likely that these
  subsystems may coordinate with each other to have the best detector performance. A higher intrument level abstraction may be
  needed. Keep this in mind while doing the system design.
## daq
I wanna rewrite the daq code based on our system design. In addition, achieve the
  following goals: 1) the core should be c/c++ based, with embeded deployment in mind; 2) ui layer is just an adaptor and may
  be needed both locally and remotely; 3) there should be a solid and robust device state machine underneath, and it should be
  service-oriented; 4) inter-process and inter-machine control/status interface needed, using web-technology; 4) the streaming
  data should be persisted immediately as well as fed into consumer pipeline for online preprocess, reconstruction and
  analysis; 5) multiple consumers maybe there and maybe disconnected without notice.
  1. draft the DAQ host-side state machine as a formal transition table
  2. draft the service API contract for control, status, metrics, and stream subscriptions
  3. scaffold the daq/ C++ directory layout and first interfaces

# management
## multi-repo coordinatin
west (https://docs.zephyrproject.org/latest/develop/west/index.html) seems to be very nice tool for management of this complex 

## ci/cd

## test

# plan
 
# system architecture and design
## domain boundary
## data contract
## adaptor
