# Tool Rack

The tool rack holds the three screwdrivers at fixed, known positions so the UR5e can pick them up without searching for them. It is a pegboard on an aluminium frame that bolts to the back of the robot cart. Because the board's position comes from the CAD model, every tool slot is a known point in the robot's frame before any camera is used.

![Work cell with tool rack](09_figures/tool_rack_cad.png)
*Figure 1. CAD of tool rack without UR5e showing pegboard and extrusions*

## Requirements it serves

- **R4**: three distinct tools, each with its own fixed slot.
- **R5**: correct tool picked up in ≥ 96% of attempts. Fixed slots mean the arm goes to a known pose, and the camera only confirms which tool is there.
- **R1**: delivery and return each ≤ 15 s. Board distance affects pickup → handover time; see [exp-001](../simulation/06_experiments/exp-001-pegboard-distance/).

## What's in this folder

| Folder | Contents |
|---|---|
| [`02_decisions/`](02_decisions/) | [Pegboard](02_decisions/pegboard.md) · [Fixed position](02_decisions/fixed-position.md) · [Frame and brackets](02_decisions/frame-and-brackets.md) · [Adjustable arms](02_decisions/adjustable-arms.md) |
| [`03_calculations/`](03_calculations/) | Reach check and arm-length worksheets |
| [`04_design/`](04_design/) | Key dimensions, interfaces, CAD (STEP + Onshape), BOM |
| [`06_experiments/build-log/`](06_experiments/build-log/) | Build status, photos and notes |
| [`09_figures/`](09_figures/) | CAD renders and drawings used in this section |

## Open issues

- **Reach margin.** The arms start at 35 cm, the fastest position in exp-001. The sim reached the board at −0.05 m but not at −0.07 m, which leaves about 2 cm of margin, and that study didn't move the board in the collision model. Re-check in the sim before final cuts.
- **The CAD doesn't match the build.** The CAD uses 45 mm uprights and 405 mm arms; the build uses 30 mm extrusion, custom brackets and 35 cm arms. Update the CAD and the sim meshes once the frame is built.
- **The fabrication milestone slipped** from Oct 30. [TBD: one honest sentence on why]
- **Return zone.** Planned under `tool-pickup`. Check that it ends up documented somewhere.

## Next steps

1. Finish the brackets and assemble the frame at 35 cm.
2. 3D print the hooks and fix the slot positions.
3. Measure the as-built position against the CAD.
4. Adjust the arm length if the camera needs a different view of the tools, then lock it.
