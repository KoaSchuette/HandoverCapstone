# handover_cell

The work cell for the capstone: mobile base, tool pegboard and a UR5e bolted on
top, ready for Gazebo, RViz and MoveIt. Exported from
`Capstone Assembly Actual.step` (Fusion).

## Run it (inside the dev container)

```bash
cd /workspaces/HandoverCapstone
colcon build --packages-select handover_cell
source install/setup.bash

# quick look, RViz only, with joint sliders
ros2 launch handover_cell view_cell.launch.py

# full sim: Gazebo + MoveIt + RViz
ros2 launch handover_cell cell_sim.launch.py
```

## Frames

```
world (floor, directly under the robot plate)        +X right, +Y toward pegboard, +Z up
 ├── ground_plane
 └── cell_base            base frame + casters + 225 mm robot plate
      ├── robot_mount     (0, 0, 0.788)   top centre of the plate
      │    └── base_link ... tool0         UR5e
      └── pegboard_frame  uprights + tie bars
           └── pegboard
                └── pegboard_face   (0.005, 0.508, 1.068)  centre of the face toward the robot
```

The arm can reach the whole pegboard: its corners are 0.55 to 0.61 m from the
shoulder (UR5e reach is 0.85 m).

## Files

| Path | What it is |
|---|---|
| `urdf/handover_cell_macro.xacro` | the cell links (meshes, collision, mass) and the two reference frames |
| `urdf/handover_cell.urdf.xacro` | cell + UR5e, used by Gazebo and RViz |
| `srdf/handover_cell.srdf.xacro` | tells MoveIt which bolted-together parts to ignore for collisions |
| `launch/cell_sim.launch.py` | Gazebo + MoveIt + RViz (wraps `ur_simulation_gz`) |
| `launch/cell_moveit.launch.py` | MoveIt with the cell-aware SRDF |
| `launch/view_cell.launch.py` | RViz-only viewer |
| `meshes/visual/*.stl` | detailed meshes, metres, already in the world frame |
| `meshes/collision/*.stl` | one box per CAD part, for fast collision checking |

## Changing things

- **Arm faces the wrong way:** add `robot_yaw:=1.5708` (radians) to the xacro
  args, or change the default in `handover_cell.urdf.xacro`.
- **CAD changed:** re-export the meshes in the same frame (origin on the floor
  under the robot plate centre, metres) and update `robot_mount` /
  `pegboard_face` if those moved.
- **Masses** are estimates from CAD volume (aluminium for the frame, hardboard
  for the pegboard). The cell is fixed to the world, so they don't affect the
  sim much.
