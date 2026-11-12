# Skeletal tracking code: how to run it

The code lives in the ROS 2 workspace, not in this folder, so there is only one copy to keep up to date.

## Install

Follow the existing guides; nothing extra is needed for skeletal tracking.

- **RealSense D455, Docker and the dev container:** [root README](../../../README.md). Plug the camera into a USB 3 port.
- **Linux host with a GPU:** [docs/Linux_hardware.md](../../../docs/Linux_hardware.md). Use the `Linux hardware` dev container; it passes the GPU in with `--gpus=all`. The node needs CUDA.
- **More on the camera:** [docs/realsense_d455_guide.md](../../../docs/realsense_d455_guide.md).

The container image installs the Python packages in [`requirements.txt`](../../../requirements.txt) (`torch`, `ultralytics`). Then, inside the container, from the workspace root:

```bash
colcon build
source install/setup.bash
```

## Launch

Run this **from the repo root**. The node loads `models/yolo26n-pose.pt` relative to the current folder.

```bash
cd /workspaces/HandoverCapstone
ros2 launch handover_skeleton_tracking skeleton.launch.py
```

[`skeleton.launch.py`](../../../src/handover_skeleton_tracking/launch/skeleton.launch.py) starts three things:

| What | Same as |
|---|---|
| RealSense camera (colour + aligned depth, 848×480 at 30 Hz) | `ros2 launch handover_realsense realsense.launch.py` |
| Skeleton node | `ros2 run handover_skeleton_tracking skeleton_node` |
| RViz with the saved skeleton config (markers + colour image) | `rviz2 -d .../rviz/skeleton.rviz` |

It also clears `FASTDDS_BUILTIN_TRANSPORTS`. If that variable is left set to `LARGE_DATA` in the terminal, the nodes can't talk to the camera.

## Check it is working

Stand in front of the camera. In RViz you should see blue joints and bones over your body. From another sourced terminal:

```bash
ros2 topic hz /camera/camera/color/image_raw   # about 30 Hz
ros2 topic echo /skeleton/position --once      # keypoints in metres; NaN = not found
```

## Files

| File | What it does |
|---|---|
| [`src/handover_skeleton_tracking/launch/skeleton.launch.py`](../../../src/handover_skeleton_tracking/launch/skeleton.launch.py) | Starts the camera, skeleton node and RViz |
| [`src/handover_skeleton_tracking/handover_skeleton_tracking/skeleton_node.py`](../../../src/handover_skeleton_tracking/handover_skeleton_tracking/skeleton_node.py) | Runs YOLO pose on the colour image, reads depth per keypoint, publishes the skeleton and markers |
| [`src/handover_realsense/launch/realsense.launch.py`](../../../src/handover_realsense/launch/realsense.launch.py) | RealSense settings (resolution, depth alignment, larger Fast DDS shared memory) |
| [`src/handover_interfaces/msg/Skeleton.msg`](../../../src/handover_interfaces/msg/Skeleton.msg) | Skeleton message: 17 keypoints and confidences |
| [`models/yolo26n-pose.pt`](../../../models/yolo26n-pose.pt) | YOLO26n-pose weights (loaded by the node) |
