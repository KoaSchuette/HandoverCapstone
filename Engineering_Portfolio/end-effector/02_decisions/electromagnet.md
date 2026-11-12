# Electromagnet

## Decision

Use a ZYE1-P49/21 electromagnet (Φ49 mm, 12 V, 0.84 A, rated 400 N) as the end effector's gripping mechanism. The magnet was supplied free by the course TA.

## Context

The end effector has to pick up steel-shafted screwdrivers from the rack, hold them up to the 0.45 kg limit in R3, and release them to a person. Two constraints bounded the choice:

- **Size.** The gripper has to fit within the 63 mm diameter of the robot's mounting flange.
- **Power.** It has to run from the robot's I/O: 24 V or lower, under 1 A continuous.

No formal decision analysis table was made when the magnet was chosen, but the team did compare the three mechanisms below. The weighted table was scored afterwards to record that comparison.

## Options considered

| Option | For | Against |
|---|---|---|
| Suction cup | No contact force on the tool, simple release | Needs a vacuum source and air line; round shafts and handles seal poorly; leaks cause drops |
| Parallel-jaw gripper | Holds any rigid shape; high grip force | Moving parts and finger geometry to design; needs accurate alignment to the tool; more control and wiring |
| **Electromagnet** (chosen) | No moving parts; one on/off output; release is switching it off; no finger alignment | Steel tools only; draws power and heats while on |

### Decision analysis

Scores run from 1 (poor) to 5 (best). They are the team's estimates; none were measured.

| Criterion | Weight | Suction | Parallel jaw | Electromagnet |
|---|---|---|---|---|
| Cost | 20% | 3 | 2 | 5 |
| Design complexity | 20% | 2 | 2 | 5 |
| Gripping force | 15% | 2 | 5 | 4 |
| Versatility | 20% | 2 | 4 | 3 |
| Reliability | 25% | 2 | 3 | 4 |
| **Weighted score** | 100% | **2.2** | **3.1** | **4.2** |

Reliability carries the most weight because a dropped tool during a handover is the failure that matters most. Cost and design complexity follow, since the project budget is shared with the rack and camera and the end effector had to be built from what the team had. Gripping force has the lowest weight because the tools are light.

| Criterion | Basis for the scores |
|---|---|
| Cost | The magnet was free. Suction needs a pump or generator, cups and tubing. A parallel-jaw gripper is a purchased or custom-built mechanism. |
| Design complexity | The magnet is one output and a driver circuit. Suction adds pneumatics. A jaw gripper adds finger design, alignment and motion control. |
| Gripping force | A jaw gripper sets its own force. The magnet's force on a screwdriver shaft is limited by the shaft, about 28 N, which is still above the required force (see [magnet feasibility](../03_calculations/magnet-feasibility.md)). Suction on a round surface is weakest. |
| Versatility | A jaw gripper handles any shape in its stroke. The magnet handles any steel tool but nothing else. Suction needs a flat, sealable surface. |
| Reliability | The magnet has no moving parts and no seal. Its weakness is heating. A seal leak drops a tool held by suction. A jaw gripper can slip or misalign. |

## Why

The electromagnet is the simplest mechanism that meets the requirement. Every tool in the rack has a steel shaft, so its main weakness, steel only, does not apply here, and it needs no alignment with the tool beyond placing the face against the shaft. It holds the tool with a single on/off signal and releases it when the signal is removed. The 49 mm puck fits within the 63 mm mounting flange. At 12 V and 0.84 A it is within the robot's power limits once the supply is stepped down (see [power architecture](power-architecture.md)).

The magnet was also available at no cost, so no purchase was needed.

## Reflection

The magnet is considerably more powerful than this application requires. It is rated for 400 N against a heaviest tool weight of 4.41 N, and the shaft limits the usable force to about 28 N. A smaller magnet would be less conspicuous on the end effector, would dissipate less heat, and would likely have been actuated safely from the tool power supply. The thermal behaviour is recorded as an open issue in the [README](../README.md).

The choice remains justified. The magnet was available at no cost, and the control box power route used with it avoided purchasing an M8 8-pin cable for the tool I/O connector.
