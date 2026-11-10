# Subsystem Guide
 
A map of every subsystem in this portfolio and where its files are. The real content lives in the folders; this page only links to it. For the project overview, see the [main README](README.md).
 
**How to use it:** find the subsystem, then follow the links in its row. The design overview, which explains how the subsystem works, is the README at the top of its Design folder.
 
**Keeping it current:** whoever adds or renames a folder updates the row here in the same commit.
 
## Components
 
| Subsystem | Owner | Status | Scope | Files |
|---|---|---|---|---|
| `end-effector` | Ryan Donen | TBD | Electromagnet end effector: driver and power circuit, brackets, wire clamps, control box board mount | [Design](04_design/end-effector/) · [Req](01_requirements/end-effector/) · [Decisions](02_decisions/end-effector/) · [Calcs](03_calculations/end-effector/) · [Code](05_code/end-effector/) · [Experiments](06_experiments/end-effector/) · [Data](07_data/end-effector/) |
| `tool-detection` | TBD | TBD | Eye-in-hand camera, calibration, YOLO model | [Design](04_design/tool-detection/) · [Req](01_requirements/tool-detection/) · [Decisions](02_decisions/tool-detection/) · [Calcs](03_calculations/tool-detection/) · [Code](05_code/tool-detection/) · [Experiments](06_experiments/tool-detection/) · [Data](07_data/tool-detection/) |
| `tool-rack` | TBD | TBD | Pegboard tool rack and return zone: CAD and build | [Design](04_design/tool-rack/) · [Req](01_requirements/tool-rack/) · [Decisions](02_decisions/tool-rack/) · [Calcs](03_calculations/tool-rack/) · [Code](05_code/tool-rack/) · [Experiments](06_experiments/tool-rack/) · [Data](07_data/tool-rack/) |
| `voice-detection` | TBD | TBD | Command recognition model | [Design](04_design/voice-detection/) · [Req](01_requirements/voice-detection/) · [Decisions](02_decisions/voice-detection/) · [Calcs](03_calculations/voice-detection/) · [Code](05_code/voice-detection/) · [Experiments](06_experiments/voice-detection/) · [Data](07_data/voice-detection/) |
| `simulation` | TBD | TBD | Robot simulation models and scenarios | [Design](04_design/simulation/) · [Req](01_requirements/simulation/) · [Decisions](02_decisions/simulation/) · [Calcs](03_calculations/simulation/) · [Code](05_code/simulation/) · [Experiments](06_experiments/simulation/) · [Data](07_data/simulation/) |
| `ros-system` | TBD | TBD | ROS architecture, nodes, configuration and motion planning. The ROS code is in its own repository: *add link and commit hash here* | [Design](04_design/ros-system/) · [Req](01_requirements/ros-system/) · [Decisions](02_decisions/ros-system/) · [Calcs](03_calculations/ros-system/) · [Code](05_code/ros-system/) · [Experiments](06_experiments/ros-system/) · [Data](07_data/ros-system/) |
 
## Integrations
 
Work that combines two or more components goes in a folder named with the `int-` prefix, for example `int-rack-to-robot`. Experiments that involve several subsystems go under the integration's name, not under any one component. Add a row here when the first folder is created.
 
| Subsystem | Owner | Status | Scope | Files |
|---|---|---|---|---|
| *(none yet)* | | | | |
 
Planned integrations, following the three subroutines in the project proposal: `int-rack-to-robot`, `int-robot-to-human`, `int-workbench-to-robot`.
 
## Whole system
 
| Subsystem | Owner | Status | Scope | Files |
|---|---|---|---|---|
| `~system` | TBD | TBD | The complete request, retrieve, hand over and return cycle | [Design](04_design/~system/) · [Req](01_requirements/~system/) · [Decisions](02_decisions/~system/) · [Calcs](03_calculations/~system/) · [Code](05_code/~system/) · [Experiments](06_experiments/~system/) · [Data](07_data/~system/) |