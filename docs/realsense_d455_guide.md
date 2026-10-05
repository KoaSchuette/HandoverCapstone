

Realsense d455 guide · MD
# RealSense D455 in ROS 2 Jazzy: publishing raw camera data
 
Suggested location in the repo: `docs/realsense_d455_guide.md`
 
## Overview
 
Intel's official ROS 2 wrapper (`realsense2_camera`) already is a "node that reads and publishes raw data from a RealSense." Writing our own driver would mean re-implementing hardware timestamps, camera_info calibration, depth/color alignment, IMU fusion and reconnect handling. So the plan is:
 
1. **Part 1:** Install the official driver in the container and verify the D455 streams.
2. **Part 2:** Create our own package, `handover_realsense`, holding our launch file, our chosen stream settings, and a small monitor node. The rest of the project depends on this package, not on the driver directly.
3. **Part 3 (optional learning exercise):** Write a minimal driver of our own with `pyrealsense2`, to understand what the official node does.
Status of the upstream project (checked October 2026): the RealSense repos have moved to the **RealSenseAI** GitHub organisation (old `IntelRealSense/...` links should redirect). The `realsense-ros` release notes list Ubuntu 24.04 support for the Jazzy distro as of build 4.56.1. Always check the current README for the install method before changing versions.
 
The D455 provides: left/right IR stereo (global shutter), depth, an RGB camera, and a built-in IMU (gyro + accelerometer). It needs a **USB 3** port and cable.
 
---
 
## Part 0: Host and container prerequisites (Ubuntu host)
 
### On the host, once
 
1. Plug the D455 into a USB 3 port (blue port or USB-C 3.x) with the supplied cable.
2. Check it enumerates at USB 3 speed:
```bash
   lsusb | grep -i intel
   lsusb -t        # the RealSense should show 5000M, not 480M
```
   If it shows 480M you are on USB 2: change the port or the cable. Many "missing stream" problems are this.
3. Install the RealSense **udev rules** on the host so a non-root user can access the device. The librealsense Linux setup docs describe the `99-realsense-libusb.rules` file, or install the `librealsense2-udev-rules` package from Intel's apt repository. Then:
```bash
   sudo udevadm control --reload-rules && sudo udevadm trigger
```
   (Unplug and replug the camera afterwards.)
 
### In the container
 
- **USB access:** The RealSense re-enumerates on the USB bus when streaming starts, so its device node can change while running. Passing a single `--device=/dev/bus/usb/001/005` is therefore unreliable. Use a mount of `/dev` (or at least `/dev/bus/usb`) together with `--privileged`, or the equivalent in `devcontainer.json` (`runArgs` / `mounts`).
- **Dockerfile:** add the packages so everyone gets them (make this change on a branch and open a PR):
```dockerfile
  RUN apt-get update && apt-get install -y \
      ros-jazzy-realsense2-camera \
      ros-jazzy-realsense2-description \
      ros-jazzy-rviz2 \
      ros-jazzy-rqt-image-view \
      usbutils \
      && rm -rf /var/lib/apt/lists/*
```
  Then rebuild the image / "Dev Containers: Rebuild Container".
- Which devcontainer config to use (`default` vs `linux-gpu`) does not matter for the RealSense itself; either works as long as USB is passed through.
> Note: I could not read the repo's `.devcontainer` files when writing this, so check that `runArgs`/`mounts` already pass USB through. If not, add it in the same PR.
 
---
 
## Part 1: Verify the official driver
 
Inside the container:
 
```bash
source /opt/ros/jazzy/setup.bash
ros2 launch realsense2_camera rs_launch.py
```
 
In a second terminal:
 
```bash
ros2 topic list
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/depth/image_rect_raw
ros2 run rqt_image_view rqt_image_view     # needs GUI forwarding; or use rviz2
```
 
By default the node name and namespace are both `camera`, so topics usually appear under `/camera/camera/...`. Older docs show `/camera/color/image_raw`; trust `ros2 topic list` on your install.
 
Expected raw topics for the D455:
 
| Topic (under `/camera/camera/`) | Type | What it is |
|---|---|---|
| `color/image_raw`, `color/camera_info` | `sensor_msgs/Image`, `CameraInfo` | RGB image + intrinsics |
| `depth/image_rect_raw`, `depth/camera_info` | `sensor_msgs/Image` (16UC1, millimetres) | Raw depth |
| `infra1/image_rect_raw`, `infra2/image_rect_raw` | `sensor_msgs/Image` | Left/right IR |
| `aligned_depth_to_color/image_raw` | `sensor_msgs/Image` | Depth registered to the colour frame (needs `align_depth.enable`) |
| `gyro/sample`, `accel/sample`, `imu` | `sensor_msgs/Imu` | IMU (needs `enable_gyro`/`enable_accel`; `imu` needs `unite_imu_method`) |
| `depth/color/points` | `sensor_msgs/PointCloud2` | Point cloud (needs `pointcloud.enable`) |
 
List every launch argument your installed version supports:
 
```bash
ros2 launch realsense2_camera rs_launch.py --show-args
```
 
Parameter names have changed between versions (for example `depth_module.profile` vs `depth_module.depth_profile`, and `align_depth` became `align_depth.enable`), so treat `--show-args` as the source of truth.
 
---
 
## Part 2: Our own package, `handover_realsense`
 
Always branch first:
 
```bash
cd /workspaces/HandoverCapstone
git checkout main && git pull
git checkout -b feature/realsense-node
```
 
Create the package (matches the `ros2 pkg create` pattern in `notes.txt`):
 
```bash
cd src
ros2 pkg create handover_realsense --build-type ament_python \
  --dependencies rclpy sensor_msgs --node-name raw_monitor
mkdir -p handover_realsense/launch
```
 
Add runtime dependencies to `src/handover_realsense/package.xml`:
 
```xml
<exec_depend>realsense2_camera</exec_depend>
<exec_depend>launch</exec_depend>
<exec_depend>launch_ros</exec_depend>
```
 
### Launch file: `launch/realsense.launch.py`
 
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
 
 
def generate_launch_description():
    rs_launch = os.path.join(
        get_package_share_directory('realsense2_camera'), 'launch', 'rs_launch.py')
 
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rs_launch),
            launch_arguments={
                'camera_name': 'camera',
                'camera_namespace': 'camera',
                # Matching depth + colour resolution makes alignment cheap.
                # Verify the parameter names with: ros2 launch realsense2_camera rs_launch.py --show-args
                'depth_module.depth_profile': '848x480x30',
                'rgb_camera.color_profile': '848x480x30',
                'align_depth.enable': 'true',
                'enable_gyro': 'true',
                'enable_accel': 'true',
                'unite_imu_method': '2',      # publish a single combined /imu topic
                'pointcloud.enable': 'false', # turn on only when needed (heavy)
            }.items(),
        ),
    ])
```
 
### Monitor node: `handover_realsense/raw_monitor.py`
 
This subscribes to the raw topics and reports what it receives. It is also your first look at **QoS**: RealSense publishes image topics with a sensor-style (best effort) profile, so a subscriber using the default reliable QoS silently receives nothing. Use `qos_profile_sensor_data`.
 
```python
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, Imu
 
 
class RawMonitor(Node):
    def __init__(self):
        super().__init__('raw_monitor')
        self.counts = {'color': 0, 'depth': 0, 'imu': 0}
        ns = 'camera/camera'
        self.create_subscription(
            Image, f'{ns}/color/image_raw',
            lambda m: self.bump('color', m), qos_profile_sensor_data)
        self.create_subscription(
            Image, f'{ns}/depth/image_rect_raw',
            lambda m: self.bump('depth', m), qos_profile_sensor_data)
        self.create_subscription(
            Imu, f'{ns}/imu',
            lambda m: self.bump('imu', m), qos_profile_sensor_data)
        self.create_timer(2.0, self.report)
 
    def bump(self, key, msg):
        if self.counts[key] == 0 and isinstance(msg, Image):
            self.get_logger().info(
                f'first {key}: {msg.width}x{msg.height} {msg.encoding} '
                f'frame_id={msg.header.frame_id}')
        self.counts[key] += 1
 
    def report(self):
        rates = {k: v / 2.0 for k, v in self.counts.items()}
        self.get_logger().info(
            'Hz  color={color:.1f}  depth={depth:.1f}  imu={imu:.1f}'.format(**rates))
        self.counts = {k: 0 for k in self.counts}
 
 
def main():
    rclpy.init()
    rclpy.spin(RawMonitor())
    rclpy.shutdown()
```
 
(If `ros2 pkg create` already generated a placeholder `raw_monitor.py`, replace its contents.)
 
### Install the launch file: `setup.py`
 
Add to `data_files`:
 
```python
import os
from glob import glob
# ...
data_files=[
    ('share/ament_index/resource_index/packages', ['resource/handover_realsense']),
    ('share/handover_realsense', ['package.xml']),
    (os.path.join('share', 'handover_realsense', 'launch'), glob('launch/*.py')),
],
```
 
### Build and run
 
```bash
cd /workspaces/HandoverCapstone
colcon build --packages-select handover_realsense --symlink-install
source install/setup.bash
 
# Terminal 1
ros2 launch handover_realsense realsense.launch.py
 
# Terminal 2
source install/setup.bash
ros2 run handover_realsense raw_monitor
```
 
Success looks like the monitor printing about 30 Hz for color and depth and 100+ Hz for the IMU. Check the pixel format with `ros2 topic echo --once /camera/camera/depth/image_rect_raw --no-arr`.
 
### Troubleshooting
 
| Symptom | Likely cause |
|---|---|
| `No RealSense devices were found` | USB not passed into the container; udev rules missing on host; try replugging |
| Streams drop or low FPS, "USB 2.1" warning | Using a USB 2 port or cable |
| Monitor prints nothing but `ros2 topic list` shows topics | QoS mismatch (use `qos_profile_sensor_data`) or wrong topic namespace |
| Launch error about an unknown argument | Parameter names differ in your version; run `--show-args` |
| Camera works once, then not after a container restart | Another process (or the old container) still holds the device |
| Depth looks noisy or has holes | Expected on shiny/dark surfaces; the D455 works best around 0.6 m or more |
 
### Commit
 
```bash
git status                       # make sure build/ install/ log/ are not listed
git add src/handover_realsense
git commit -m "Add handover_realsense package: launch file and raw stream monitor"
git push -u origin feature/realsense-node
```
 
Put the Dockerfile and devcontainer changes in the same PR, then ask a teammate for a review before merging.
 
---
 
## Part 3 (optional): a minimal driver of your own with `pyrealsense2`
 
Do this only to learn what the official node does. For the real system, use the official driver.
 
Important constraints:
 
- **Only one process can own the camera.** Stop the official driver before running this.
- Install the bindings: `pip install pyrealsense2` (check that a wheel exists for the container's Python, which is 3.12 on Jazzy). Add it to `requirements.txt` if you keep it.
- This version stamps frames with the ROS clock at arrival time. The official driver uses the camera's hardware timestamps, which matters for sensor fusion. It also publishes no `camera_info`, so intrinsics would be missing.
Add `d455_raw = handover_realsense.d455_raw:main` under `console_scripts` in `setup.py`, then create `handover_realsense/d455_raw.py`:
 
```python
import numpy as np
import pyrealsense2 as rs
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
 
 
class D455Raw(Node):
    def __init__(self):
        super().__init__('d455_raw')
        self.color_pub = self.create_publisher(Image, 'color/image_raw', qos_profile_sensor_data)
        self.depth_pub = self.create_publisher(Image, 'depth/image_raw', qos_profile_sensor_data)
 
        cfg = rs.config()
        cfg.enable_stream(rs.stream.color, 848, 480, rs.format.rgb8, 30)
        cfg.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
        self.pipe = rs.pipeline()
        self.pipe.start(cfg)
 
        self.create_timer(1.0 / 60.0, self.tick)   # poll faster than the frame rate
 
    @staticmethod
    def to_msg(arr, encoding, stamp, frame_id):
        msg = Image()
        msg.header.stamp = stamp
        msg.header.frame_id = frame_id
        msg.height, msg.width = arr.shape[:2]
        msg.encoding = encoding
        msg.is_bigendian = 0
        msg.step = arr.strides[0]
        msg.data = arr.tobytes()
        return msg
 
    def tick(self):
        frames = self.pipe.poll_for_frames()
        if not frames:
            return
        stamp = self.get_clock().now().to_msg()
        color = frames.get_color_frame()
        depth = frames.get_depth_frame()
        if color:
            self.color_pub.publish(self.to_msg(
                np.asanyarray(color.get_data()), 'rgb8', stamp, 'camera_color_optical_frame'))
        if depth:
            self.depth_pub.publish(self.to_msg(
                np.asanyarray(depth.get_data()), '16UC1', stamp, 'camera_depth_optical_frame'))
 
    def destroy_node(self):
        self.pipe.stop()
        super().destroy_node()
 
 
def main():
    rclpy.init()
    node = D455Raw()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
```
 
Run it with `ros2 run handover_realsense d455_raw` and inspect with `ros2 topic hz /color/image_raw`.
 
---
 
## What comes next in the project
 
- Record a short rosbag of color, depth, camera_info and imu (`ros2 bag record`) so teammates without the camera, including Windows users, can develop perception code against real data.
- Publish a static transform from the robot base to `camera_link` once the camera is mounted (later replaced by hand-eye calibration).
- Feed `aligned_depth_to_color/image_raw` into the tool detection step (AprilTags or a detection model).
## Sources
 
- RealSense ROS wrapper: github.com/IntelRealSense/realsense-ros (organisation now RealSenseAI) and its releases page
- `realsense2_camera` Jazzy API docs: docs.ros.org/en/ros2_packages/jazzy/api/realsense2_camera
- RealSense SDK: github.com/realsenseai/librealsense
