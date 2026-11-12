# Tool Rack

The tool rack holds the three screwdrivers at fixed, known positions so the UR5e can pick them up without searching for them. It is a pegboard on an aluminium frame that bolts to the back of the robot cart. Because the board's position comes from the CAD model, every tool slot is a known point in the robot's frame before any camera is used.

![Work cell with tool rack](09_figures/tool_rack_cad.PNG)
*Figure 1. CAD of tool rack without UR5e showing pegboard and extrusions*

## Requirements it serves

- **R4**: three distinct tools, each with its own fixed slot.
- **R5**: correct tool picked up in ≥ 96% of attempts. Fixed slots mean the arm goes to a known pose, and the camera only confirms which tool is there.
- **R1**: delivery and return each ≤ 15 s. The board's distance sets how far the base turns between the pickup and the staging pose, where the robot holds the tool and waits for the operator's hand. See the [pegboard-distance](06_experiments/pegboard-distance/).

## What's in this folder

| Folder | Contents |
|---|---|
| [`02_decisions/`](02_decisions/) | [Pegboard](02_decisions/pegboard.md) · [Fixed position](02_decisions/fixed-position.md) · [Frame and brackets](02_decisions/frame-and-brackets.md) · [Adjustable arms](02_decisions/adjustable-arms.md) |
| [`03_calculations/`](03_calculations/) | [Reach-limit worksheet](03_calculations/reach-limit-worksheet.png): how close the board can get before the arm can't reach the pickup pose |
| [`04_design/`](04_design/) | [Design notes](04_design/README.md): board position in the robot's frame, interfaces, CAD (STEP) and [BOM](04_design/BOM.md) |
| [`06_experiments/`](06_experiments/) | [Pegboard distance study](06_experiments/pegboard-distance/): pickup → staging time against board distance, and the reach limit |
| Code | [`handover_cell`](https://github.com/KoaSchuette/HandoverCapstone/tree/7ac949a/src/handover_cell): cell model with the pegboard frame, the `pegboard_face` frame the robot targets, and the `pegboard_offset` setting that moves the board · [`handover_demo.py`](https://github.com/KoaSchuette/HandoverCapstone/blob/7ac949a/src/handover_cell/scripts/handover_demo.py): the script that ran the distance study |

## Return zone

The return zone is where the operator sets a tool down for the robot to put back on the rack. It is on the robot's base (the top of the cart), on the side opposite the arm. Because it is part of the cart, like the board, its position comes from the CAD and doesn't change during operation (see [fixed position](02_decisions/fixed-position.md)).

## Open issues

- **Reach margin.** The arms start at 35 cm, the fastest position in pegboard-distance. The sim reached the board at −0.05 m. -0.07 m was tested and works, but the arm is folded almost back on itself there, and the sim has no gripper or camera on the wrist. Re-check in the sim before final cuts.
- **The CAD doesn't match the build.** The CAD uses 45 mm uprights and 405 mm arms; the build uses 30 mm extrusion, custom brackets, and longer arms set at 35 cm until the final length is chosen. Update the CAD and the sim meshes once the frame is built.
- **The fabrication milestone slipped** from Oct 30. We waited for the ordered parts to arrive so we could confirm the build before starting any 3D prints. The brackets join two different extrusion sizes, so printing them early risked reprinting if the parts didn’t match the CAD. The hooks and brackets are printed once the frame parts are in.

## Next steps

1. Finish the brackets and assemble the frame with the board at 35 cm.
2. 3D print the hooks and fix the slot positions.
3. Measure the as-built position against the CAD.
4. Adjust the arm length if the camera needs a different view of the tools, then cut the arms to that length.
