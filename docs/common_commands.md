# Common commands

Quick reference for the commands used most often. A plain-text copy for copy-pasting is in [common_commands.txt](common_commands.txt); keep both in sync.

Run everything **inside the dev container**, from the repo root, unless it says **host**. Setup is in [setup_linux.md](setup_linux.md).

## Build and source

Build the whole workspace, or one package, then source it in every new terminal:

```bash
cd /workspaces/HandoverCapstone
colcon build                                          # everything
colcon build --packages-select handover_hand_tracking # one package
source install/setup.bash
```

## Make a new package

**Python package with a starter node:**

```bash
cd /workspaces/HandoverCapstone/src
ros2 pkg create handover_voice --build-type ament_python --dependencies rclpy std_msgs --node-name command_listener
#               └ package name                                                          └ node name
```

**Custom messages and services:** add them to the existing `handover_interfaces` package rather than making a new one.

1. Put the file in `src/handover_interfaces/msg/` (e.g. `MyMsg.msg`) or `srv/` (e.g. `MySrv.srv`).
2. Add it to `rosidl_generate_interfaces(...)` in [`src/handover_interfaces/CMakeLists.txt`](../src/handover_interfaces/CMakeLists.txt). Add any new message dependencies to `DEPENDENCIES` there and to `package.xml`.
3. Rebuild and check:

   ```bash
   colcon build --packages-select handover_interfaces
   source install/setup.bash
   ros2 interface show handover_interfaces/msg/MyMsg
   ```

To make a new interfaces package from scratch instead (CMake is required for messages):

```bash
ros2 pkg create my_interfaces --build-type ament_cmake
```

## Ultraleap (hand tracking)

The tracking service runs on the **host**. To check it's seeing your hand, open the control panel on the host:

```bash
ultraleap-hand-tracking-control-panel   # host
```

In the container:

```bash
ros2 run handover_hand_tracking leap_node                    # node only: publishes /hand/right and /hand/left
ros2 launch handover_hand_tracking hand_tracking.launch.py   # node + RViz
```

If `leap_node` fails with `No module named 'leap'`, see [setup_linux.md, step 7](setup_linux.md#if-the-ultraleap-bindings-are-missing).

## RealSense camera

```bash
ros2 launch handover_realsense realsense.launch.py   # camera only: colour + aligned depth, 848x480 at 30 Hz
ros2 run rqt_image_view rqt_image_view               # view /camera/camera/color/image_raw
```

## Skeleton tracking

Run these **from the repo root**: the node loads `models/yolo26n-pose.pt` relative to the current folder. Needs an NVIDIA GPU.

```bash
cd /workspaces/HandoverCapstone
ros2 run handover_skeleton_tracking skeleton_node             # node only (start the RealSense separately)
ros2 launch handover_skeleton_tracking skeleton.launch.py     # RealSense + node + RViz
```

## Bringup: the full handover stack

One launch file starts the UR driver, MoveIt, RViz, the motion planner and the Ultraleap node. Pick a mode:

| Mode | What it does | Command |
|---|---|---|
| `mock` | No robot. The UR driver uses mock hardware, so the arm only moves in RViz. Use it to test planning safely. | `ros2 launch handover_bringup handover.launch.py mode:=mock` |
| `real` | Moves the real UR5e. Needs the robot IP, and the External Control program running on the teach pendant. Keep the e-stop within reach. | `ros2 launch handover_bringup handover.launch.py mode:=real robot_ip:=192.168.1.102` |

Everything above the UR driver behaves the same in both modes.

**Mock:**

```bash
ros2 launch handover_bringup handover.launch.py mode:=mock
```

**Real:**

```bash
ros2 launch handover_bringup handover.launch.py mode:=real robot_ip:=192.168.1.102
```

**Template with every argument** (defaults shown; change what you need):

```bash
ros2 launch handover_bringup handover.launch.py mode:=mock robot_ip:= use_rviz:=true use_leap:=true
```

| Argument | Default | Meaning |
|---|---|---|
| `mode` | `mock` | `mock` or `real` |
| `robot_ip` | (empty) | Robot IP; required for `mode:=real` |
| `use_rviz` | `true` | `false` = no RViz |
| `use_leap` | `true` | `false` = no Ultraleap node. Nothing publishes a hand then, so a handover will wait forever. |

**Start a handover** (second terminal, sourced), with your right hand held still over the Ultraleap:

```bash
ros2 service call /start_handover std_srvs/srv/Trigger
```

## Handy checks

```bash
ros2 node list
ros2 topic list
ros2 topic hz /camera/camera/color/image_raw
ros2 topic echo /hand/right --once
ros2 topic echo /skeleton/position --once
```
