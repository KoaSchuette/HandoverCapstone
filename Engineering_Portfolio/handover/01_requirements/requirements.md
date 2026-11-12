# Handover requirements

These requirements break the project requirements (R1, R2, R6 in the [portfolio start page](../../START_HERE.md)) down to the handover leg: from "robot is holding the tool at the staging pose" to "operator has the tool". Picking the tool up is `tool-pickup`; holding it securely (R3) is `end-effector`.

Numbers either trace to a source in the **Source** column or are marked **TBD**. Values that come from current code are tuning values, not requirements, until a test or source backs them.

## Requirements

| ID | Requirement | Value | Parent | Source | Verified by |
|---|---|---|---|---|---|
| H1 | The handover motion, from the robot starting to move toward the hand to the tool arriving at the hand, is short enough to fit the delivery time budget | ≤ 2 s (does not include the steady-hand wait, IK time or release) | R1 (15 s delivery limit, 5 s target) | Team target, set 2026-11-11 | T1 |
| H2 | The operator takes the tool successfully | ≥ 80% of trials (target 90%) | R2 | Main README | T2 |
| H3 | The tool arrives at the hand with zero velocity and zero acceleration (the robot slows to a stop at the hand) | Zero at end of path | Project description ("slowing as it approaches") | Quintic time law [1] | Calc (section 2) |
| H4 | The tool approaches the hand from the palm side, along the palm normal | Final path tangent parallel to the palm normal | R2 | Biagi et al. [1] | Calc (section 1) + T2 |
| H5 | The tool is released only when the operator pulls on it | Pull threshold TBD; must sit clearly above the force sensor's noise (UR5e TCP sensor precision ±3.5 N, accuracy ±4.0 N [2]) | R2 | [2] | T2 |
| H6 | The tool is presented in an orientation the operator can grasp by the handle | Per-tool grasp offset TBD | R2 | Biagi et al. [1] | T2 |

## Test plan

| Test | What | How | Pass |
|---|---|---|---|
| T1 | Handover motion time | On the real robot, log when the trajectory starts executing and when the controller reports it finished, for each tool. Also log the steady-hand wait and IK time separately, so the full handover time is known. | Motion ≤ 2 s (H1) |
| T2 | Handoff success | Part of the final evaluation: 48 delivery trials (4 operators x 3 tools x 4 repetitions). A trial passes if the operator holds the tool a=nd the robot has released it with no regrasp, drop or abort. | ≥ 80% (H2) |

## Sources

1. F. Biagi, D. Onfiani, S. Silenzi, C. Iani, L. Biagiotti, "Adaptive vs. Static Robot-to-Human Handover: A Study on Orientation and Approach Direction," arXiv:2604.22378, Apr. 2026. Sections III-C and III-D.
2. Universal Robots, UR5e datasheet, force sensing (tool flange): range ±50.0 N, precision ±3.5 N, accuracy ±4.0 N. https://cdn.elmark.com.pl/34833

> **Check:** H5 assumes the pull is measured with the UR5e's built-in tool flange force/torque sensor. If the end effector uses a separate sensor, replace source [2] with its datasheet.
