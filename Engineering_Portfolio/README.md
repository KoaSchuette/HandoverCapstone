# Collaborative Robotic Tool Handover System: Engineering Portfolio
 
MREN 403, Group 16, Queen's University (Smith Engineering)
 
This repository is the engineering portfolio for our capstone project. It is the technical record of the work: requirements, decisions, calculations, designs, code, experiments, and data. It is meant to be understood by teammates, or the next engineer(s) who may continue using the platform after the project ends.
 
> **New here? Start with [SUBSYSTEMS.md](SUBSYSTEMS.md).** It lists every subsystem with links to its files in each folder.
 
## The project
 
A collaborative robot assistant for manufacturing work cells. Working beside a single operator at a fixed workbench, a UR5e arm:
 
1. **Rack to robot:** takes a spoken request, identifies the requested screwdriver on the tool rack with a camera, and picks it up with an electromagnetic end effector.
2. **Robot to human:** brings the tool to the operator's hand, slowing as it approaches, and releases it when the operator has grasped it.
3. **Workbench to robot, then robot to rack:** when the operator places a tool in the return zone, identifies it, picks it up and puts it back in its place on the rack.
### Headline requirements
 
Full list, justifications and test plans are in each subsystem's `01_requirements/` folder and the project proposal.
 
| ID | Requirement |
|---|---|
| R1 | Delivery and return each completed in 15 s or less (target 5 s) |
| R2 | Successful handoff in at least 80% of trials (target 90%) |
| R3 | Securely hold payloads up to 0.45 kg with no slip during motion |
| R4 | Identify, deliver and return three distinct tools |
| R5 | Correct tool picked up in at least 96% of attempts |
| R6 | Hand localization accurate enough for handoff (verified through R2) |
| R7 | Setup and operation documented well enough for someone outside the team to run a full cycle |
 
Final evaluation: 48 delivery and 48 return trials (4 operators x 3 tools x 4 repetitions).
 
## Repository layout
 
The portfolio is organized by subsystem. Each subsystem uses the folders below, but only the ones it needs. A folder is created once there’s something to put in it, so an empty or missing folder means that kind of work hasn’t happened yet for that subsystem. Folder names and numbers are the same everywhere, so you always know what a folder contains.
 
```
Engineering_Portfolio/
├── README.md             this file
├── SUBSYSTEMS.md         map of every subsystem and where its files are
├── 00_project/           risk register, budget, schedule, project proposal
├── end-effector/
├── tool-rack/
├── voice-detection/
├── handover/
├── skeletal-tracking/
├── tool-pickup/
└── system/               whole-system work (intentionally left empty for now)
```
 
Folders a subsystem can contain:
 
```
<subsystem>/
├── 01_requirements/      subsystem requirements
├── 02_decisions/         decision records: what we chose, why, what we rejected, how we verified it
├── 03_calculations/      hand calculations, notebooks, scripts and simulations
├── 04_design/            CAD, schematics, KiCad, architecture, interfaces
├── 05_code/              source code and scripts
├── 06_experiments/       procedures, raw results, photos, videos and build logs
├── 07_data/              raw and processed data
├── 08_references/        datasheets, manuals, papers
├── 09_figures/           polished figures used in reports and presentations
└── 10_deliverables/      reports and presentations for this subsystem
```
 
### Subsystem names
 
| Name | Scope |
|---|---|
| `end-effector` | Electromagnet end effector: driver and power circuit, brackets, wire clamps, control box board mount |
| `tool-rack` | Pegboard tool rack and return zone: CAD and build |
| `voice-detection` | Command recognition model |
| `handover` | Robot-to-human handoff: approach, slowdown and release |
| `skeletal-tracking` | Operator skeleton and hand tracking with the RealSense camera |
| `tool-pickup` | Identifying the requested tool and picking it up from the rack or return zone |
| `system` | The complete handover cycle (empty for now) |
 
Add new names to this table and to `SUBSYSTEMS.md` before creating folders for them. A new subsystem starts with a README.md and has the `01_` to `10_` folders when it has the data necessary.
