# HandoverCapstone

## Realsense Hardware setup (Linux)

Hardware work (RealSense, UR5e) needs a Linux host with Docker Engine,
not Docker Desktop, so USB devices can be passed into the container. Do these
steps on the **host**, not inside the container.

### 1. RealSense D455

1. Plug the camera directly into a **USB 3** port (no hub) with the supplied cable.
2. Check the link speed on the host:
```bash
   lsusb -t
```
   The RealSense should show `5000M`. If it shows `480M` it is on USB 2: replug it
   firmly or try another port or cable. The driver logs `Device USB type: 3.x`
   when it is healthy; `2.1` causes dropped frames and low resolution.
3. Install the udev rules so the camera can be accessed without root. Download
   `99-realsense-libusb.rules` from the librealsense repo (`config/` folder) and run:
```bash
   sudo cp 99-realsense-libusb.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules && sudo udevadm trigger
```
   Then unplug and replug the camera. If the download link has moved, follow the
   Linux installation guide in the librealsense repo.

### 2. Open the dev container

1. Install Docker Engine and the Compose plugin (see docs.docker.com/engine/install/ubuntu),
   then add yourself to the `docker` group:
```bash
   sudo usermod -aG docker $USER
```
   and log out and back in.
2. In VS Code, open the repo and run **Dev Containers: Reopen in Container**,
   choosing the `default` config (or `linux-gpu` if the machine has a GPU).
   The config runs privileged with `/dev` mounted so USB devices are visible.
3. After a Dockerfile change, run **Dev Containers: Rebuild Container**.

### 3. GUI tools (RViz, rqt)

Before launching a GUI tool from the container, allow it to use the host display.
Run this on the **host** once per login session:

```bash
xhost +local:
```

### 4. Check the camera

Inside the container:

```bash
lsusb | grep -i intel
ros2 launch realsense2_camera rs_launch.py
```

In a second terminal:

```bash
ros2 topic list
ros2 run rqt_image_view rqt_image_view   # pick /camera/camera/color/image_raw
```

### Troubleshooting

| Symptom | Fix |
|---|---|
| `No RealSense devices were found` | Udev rules missing on the host, or the container was not rebuilt after the `devcontainer.json` change. Replug the camera. |
| `Device USB type: 2.1` / corrupted-frame warnings | Camera is on a USB 2 link. Replug into a USB 3 port. |
| `could not connect to display` | Run `xhost +local:` on the host. |
| `Failed to read busnum/devnum` (HID warnings) | Usually harmless inside a container. |
