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
 
Full list, justifications and test plans are in [01_requirements/](01_requirements/) and the project proposal.
 
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
 
The top-level folders follow the course's suggested structure. Inside each folder, work is separated by subsystem, using the same subsystem names everywhere.
 
```
Engineering_Portfolio/
├── README.md             this file
├── SUBSYSTEMS.md         map of every subsystem and where its files are
├── 00_project/              risk register, budget tracking, schedule, and other project management documents 
├── 01_requirements/         system, subsystem and integration requirements
├── 02_decisions/            decision records: what we chose, why, what we rejected, how we verified it
├── 03_calculations/         hand calculations, notebooks, scripts and simulations
├── 04_design/               CAD, schematics, KiCad, architecture, and interfaces between subsystems
├── 05_code/                 source code and scripts
├── 06_experiments/          procedures, raw results, photos, videos and build logs for every test
├── 07_data/                 raw and processed data
├── 08_references/           datasheets, manuals, papers
├── 09_figures/              polished figures used in reports and presentations
└── 10_deliverables/         final report, presentations, budget statement
```
 
Each of `01_requirements/`, `02_decisions/`, `03_calculations/`, `04_design/`, `05_code/`, `06_experiments/` and `07_data/` contains one subfolder per subsystem.
 
### Subsystem names
 
| Name | Scope |
|---|---|
| `end-effector` | Electromagnet end effector: driver and power circuit, brackets, wire clamps, control box board mount |
| `ros-system` | ROS architecture, nodes, configuration and motion 
| `tool-detection` | Eye in hand camera, calibration, YOLO model |
| `tool-rack` | Pegboard tool rack and return zone: CAD and build |
| `voice-detection` | Command recognition model |
| `simulation` | Robot simulation models and scenarios |
| `~system` | The complete handover cycle |
 
Plain names are components that can be tested on their own. The `int-` prefix marks work that combines several components, and `~system` is the whole robot. Add new names to this table and to `SUBSYSTEMS.md` before creating folders for them.
