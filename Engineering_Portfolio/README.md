# Collaborative Robotic Tool Handover System: Engineering Portfolio
 
MREN 403, Group 16, Queen's University (Smith Engineering)
 
This folder contains the engineering portfolio for our capstone project. Which documents all technical record of the work: requirements, decisions, calculations, designs, code, experiments, and data.
 
> **New here? Start with the [system overview](system/README.md).** It shows how the subsystems work together over one full cycle. Then go to the subsystem you're working on in the [subsystem table](#subsystems).
 
## The project

The Collaborative Handover Assistant is a robotic tool assistant for manufacturing work cells. It works beside one operator at a fixed workbench, fetching screwdrivers on voice command, handing them over safely, and putting them back on the rack when the operator is done.

### Core functions

1. **Tool retrieval (rack to robot):** The operator asks for a tool out loud. The robot finds that screwdriver on the tool rack with a camera and picks it up with an electromagnetic end effector.
2. **Handover (robot to human):** The robot brings the tool to the operator's hand and slows down as it gets close. It releases the tool once it detects that the operator is holding it.
3. **Tool return (workbench to rack):** When the operator puts a tool in the return zone, the robot identifies it, picks it up, and puts it back in its spot on the rack.

### Headline requirements

Full list, justifications and test plans are in each subsystem's `01_requirements/` folder and the [project proposal](deliverables/project-proposal.pdf).
 
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
├── README.md         this file
├── system/               whole-system design: task state machine, node architecture (plan, not built yet)
├── 00_project/           risk register, budget, schedule (not created yet)
├── deliverables/         course deliverables as they are submitted
├── end-effector/
├── tool-rack/
├── voice-detection/
├── handover/
├── skeletal-tracking/
└── tool-pickup/
```
 
Folders a subsystem can contain:
 
```
<subsystem>/
├── 01_requirements/      subsystem requirements
├── 02_decisions/         decision records: what we chose, why, what we rejected, how we verified it
├── 03_calculations/      hand calculations, notebooks, scripts and simulations
├── 04_design/            CAD, schematics, KiCad, architecture, interfaces
├── 05_code/              source code and scripts
├── 06_experiments/       procedures, results, photos and build logs
├── 07_data/              raw and processed data, including test videos
├── 08_references/        datasheets, manuals, papers
├── 09_figures/           polished figures used in reports and presentations
└── 10_deliverables/      reports and presentations specific to this subsystem. Whole-team course deliverables go in the top-level `deliverables/` folder
```
 
## Subsystems

Start with `system`, then the subsystem you need. Each one has a start page with its overview, status and links into its folders.

| Subsystem | Owner | Status | Scope | Start page |
|---|---|---|---|---|
| `system` | Koa & Ryan Donen | Design plan; FSM not built | The complete cycle: task state machine, ROS node architecture and implementation status | [system](system/README.md) |
| `end-effector` | Ryan Donen | Prototype Built; Testing phase | Electromagnet end effector: driver and power circuit, brackets, wire relief clamps, driver circuit board mount | [end-effector](end-effector/README.md) |
| `tool-rack` | Tanner | Waiting For Parts  | Pegboard tool rack and return zone: CAD and build | [tool-rack](tool-rack/README.md) |
| `voice-detection` | Ryan Henderson | Early: Diction model testing | Command recognition model | [voice-detection](voice-detection/README.md) |
| `tool-pickup` | Tanner & Ryan Donen | Calibration done | Identifying the requested tool and picking it up from the rack or return zone | [tool-pickup](tool-pickup/README.md) |
| `handover` | Koa | Runs on the real UR5e (commit-once); moving to real-time planning | Robot-to-human handoff: approach, slowdown and release | [handover](handover/README.md) |
| `skeletal-tracking` | Koa | Early: one pose model tested | Safety: tracking people's bodies with the RealSense camera so the arm can stop if someone is in its way | [skeletal-tracking](skeletal-tracking/README.md) |

Add new names to this table before creating folders for them. A new subsystem starts with a `README.md` (overview, status, how it works, testing so far, future work, and links into its folders) and adds the `01_` to `10_` folders when it has something to put in them.

## Course deliverables

The [`deliverables/`](deliverables/) folder holds the documents the team submits for the course, kept at the same level as the subsystem folders because they belong to the whole project. Each one is added when it is completed, and the folder's [README](deliverables/README.md) lists them. So far it holds the [project proposal](deliverables/project-proposal.pdf).
