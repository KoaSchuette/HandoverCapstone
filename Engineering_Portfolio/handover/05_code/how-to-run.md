# Handover code: how to run it

The code lives in the ROS 2 workspace, not in this folder, so there is only one copy to keep up to date.

## Install

Follow the existing guides; nothing extra is needed for the handover.

- **Dev container and Docker:** [root README](../../../README.md). The container image already includes ROS 2 Jazzy, `ur_robot_driver` and MoveIt.
- **Ultraleap, graphics and USB access on a Linux host:** [docs/Linux_hardware.md](../../../docs/Linux_hardware.md). Needed for real hand tracking.

Then, inside the container, from the workspace root:

```bash
colcon build
source install/setup.bash
```

## Start the stack

Everything is started by one launch file, [`handover_bringup/launch/handover.launch.py`](../../../src/handover_bringup/launch/handover.launch.py), in either **mock** or **real** mode. It starts the UR driver, MoveIt (`move_group`, which provides `compute_ik`), RViz, the planner node and the Ultraleap node.

| Argument | Default | Meaning |
|---|---|---|
| `mode` | `mock` | `mock` runs without a robot; `real` moves the arm |
| `robot_ip` | (empty) | Robot IP, required for `mode:=real` |
| `use_rviz` | `true` | Start RViz |
| `use_leap` | `true` | Start the Ultraleap hand tracking node |

Only the UR driver's hardware plugin changes between modes, so every node above it behaves the same in mock and real.

### Mock mode (no robot)

```bash
ros2 launch handover_bringup handover.launch.py mode:=mock
```

The arm moves in RViz only. The planner still needs hand data on `/hand/right`, so the Ultraleap must be plugged in. With `use_leap:=false` nothing publishes a hand, and the steady-hand wait never finishes.

### Real mode (UR5e)

```bash
ros2 launch handover_bringup handover.launch.py mode:=real robot_ip:=192.168.1.102
```

On the teach pendant, run the External Control program so the driver can command the arm. Keep the emergency stop within reach.

## Run a handover

1. Hold your right hand open and still over the Ultraleap, palm facing the robot.
2. In a second terminal (sourced), call:

   ```bash
   ros2 service call /start_handover std_srvs/srv/Trigger
   ```

3. The planner waits for a steady hand, plans the path and sends the trajectory. The service returns `trajectory sent` once the goal is sent, not when the motion finishes. If IK or the joint-limit check fails, it returns the reason instead.

## Check the path without ROS

[`test_path.py`](../../../src/handover_motion/handover_motion/test_path.py) plots the path shape and the time-law spacing for a 2D test case:

```bash
cd src/handover_motion/handover_motion
python3 test_path.py
```

## Files

| File | What it does |
|---|---|
| [`src/handover_bringup/launch/handover.launch.py`](../../../src/handover_bringup/launch/handover.launch.py) | Starts the full stack in mock or real mode |
| [`src/handover_motion/handover_motion/planner_node.py`](../../../src/handover_motion/handover_motion/planner_node.py) | Motion planner node: steady-hand gate, path sampling, IK calls, joint-limit check, trajectory goal |
| [`src/handover_motion/handover_motion/helper.py`](../../../src/handover_motion/handover_motion/helper.py) | `bezier`, `time_law` (quintic), `find_pull_points` (control points), `find_orientation` (SLERP with lock) |
| [`src/handover_motion/handover_motion/test_path.py`](../../../src/handover_motion/handover_motion/test_path.py) | Path and time-law plot (no ROS needed) |
| [`src/handover_hand_tracking/handover_hand_tracking/leap_node.py`](../../../src/handover_hand_tracking/handover_hand_tracking/leap_node.py) | Publishes `/hand/right` and `/hand/left` from the Ultraleap (in metres, frame `leap_link`) |
| [`src/handover_interfaces/msg/Hand.msg`](../../../src/handover_interfaces/msg/Hand.msg) | Hand message definition |
