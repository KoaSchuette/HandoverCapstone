# Subsystem Guide
 
A map of every subsystem in this portfolio and where its files are. The real content lives in the folders; this page only links to it. For the project overview, see the [main README](README.md).
 
**How to use it:** find the subsystem, then follow the links in its row. Every subsystem folder has the same `01_requirements` to `10_deliverables` folders. The design overview, which explains how the subsystem works, is the README at the top of its `04_design` folder.
 

 
## Subsystems
 
| Subsystem | Owner | Status | Scope | Files |
|---|---|---|---|---|
| `end-effector` | Ryan Donen | TBD | Electromagnet end effector: driver and power circuit, brackets, wire clamps, control box board mount | [Req](end-effector/01_requirements/) · [Decisions](end-effector/02_decisions/) · [Calcs](end-effector/03_calculations/) · [Design](end-effector/04_design/) · [Code](end-effector/05_code/) · [Experiments](end-effector/06_experiments/) · [Data](end-effector/07_data/) · [Refs](end-effector/08_references/) · [Figures](end-effector/09_figures/) · [Deliverables](end-effector/10_deliverables/) |
| `tool-rack` | TBD | TBD | Pegboard tool rack and return zone: CAD and build | [Req](tool-rack/01_requirements/) · [Decisions](tool-rack/02_decisions/) · [Calcs](tool-rack/03_calculations/) · [Design](tool-rack/04_design/) · [Code](tool-rack/05_code/) · [Experiments](tool-rack/06_experiments/) · [Data](tool-rack/07_data/) · [Refs](tool-rack/08_references/) · [Figures](tool-rack/09_figures/) · [Deliverables](tool-rack/10_deliverables/) |
| `voice-detection` | TBD | TBD | Command recognition model | [Req](voice-detection/01_requirements/) · [Decisions](voice-detection/02_decisions/) · [Calcs](voice-detection/03_calculations/) · [Design](voice-detection/04_design/) · [Code](voice-detection/05_code/) · [Experiments](voice-detection/06_experiments/) · [Data](voice-detection/07_data/) · [Refs](voice-detection/08_references/) · [Figures](voice-detection/09_figures/) · [Deliverables](voice-detection/10_deliverables/) |
| `handover` | TBD | TBD | Robot-to-human handoff: approach, slowdown and release | [Req](handover/01_requirements/) · [Decisions](handover/02_decisions/) · [Calcs](handover/03_calculations/) · [Design](handover/04_design/) · [Code](handover/05_code/) · [Experiments](handover/06_experiments/) · [Data](handover/07_data/) · [Refs](handover/08_references/) · [Figures](handover/09_figures/) · [Deliverables](handover/10_deliverables/) |
| `skeletal-tracking` | TBD | TBD | Operator skeleton and hand tracking with the RealSense camera | [Req](skeletal-tracking/01_requirements/) · [Decisions](skeletal-tracking/02_decisions/) · [Calcs](skeletal-tracking/03_calculations/) · [Design](skeletal-tracking/04_design/) · [Code](skeletal-tracking/05_code/) · [Experiments](skeletal-tracking/06_experiments/) · [Data](skeletal-tracking/07_data/) · [Refs](skeletal-tracking/08_references/) · [Figures](skeletal-tracking/09_figures/) · [Deliverables](skeletal-tracking/10_deliverables/) |
| `tool-pickup` | TBD | TBD | Identifying the requested tool and picking it up from the rack or return zone | [Req](tool-pickup/01_requirements/) · [Decisions](tool-pickup/02_decisions/) · [Calcs](tool-pickup/03_calculations/) · [Design](tool-pickup/04_design/) · [Code](tool-pickup/05_code/) · [Experiments](tool-pickup/06_experiments/) · [Data](tool-pickup/07_data/) · [Refs](tool-pickup/08_references/) · [Figures](tool-pickup/09_figures/) · [Deliverables](tool-pickup/10_deliverables/) |
 
## Whole system
 
The [`system/`](system/) folder is reserved for work on the complete request, retrieve, hand over and return cycle. It is intentionally empty for now.
 
## Project management
 
[`00_project/`](00_project/) holds the risk register, budget, schedule and the project proposal.
