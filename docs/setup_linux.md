# Setup on Linux

This guide sets up a **Linux (Ubuntu) host** to run the project's dev container with the hardware attached: the Ultraleap hand tracker, the RealSense D455 camera, the GPU, and windows such as RViz and Gazebo on your screen.

ROS 2 Jazzy, the UR driver, MoveIt, the RealSense ROS driver and the Python packages are all installed **inside the container** by the [Dockerfile](../.devcontainer/Dockerfile). You don't install ROS on the host. The host only needs what the container can't do for itself:

| Step | Where | Why it has to be on the host |
|---|---|---|
| [1. Docker Engine](#1-docker-engine) | Host | Runs the container |
| [2. NVIDIA GPU (skeleton node)](#2-nvidia-gpu-skeleton-node) | Host | Gives the container the GPU |
| [3. Ultraleap](#3-ultraleap) | Host | The tracking service runs on the host; the container connects to it |
| [4. RealSense](#4-realsense) | Host | USB permissions (udev rules) are set on the host |
| [5. Graphics and display](#5-graphics-and-display) | Host | Lets the container draw windows on your screen |
| [6. Open the dev container](#6-open-the-dev-container) | VS Code | Builds and starts the container |
| [7. Verify everything](#7-verify-everything) | Container | Checks each part works |

Do the steps in order. Steps 1 to 5 happen in a normal terminal on the **host**, not inside the container.

> **Do step 3 before opening the container.** The Linux dev container mounts the Ultraleap install folder from the host. If the Ultraleap software is not installed, the container will fail to start.

---

## 1. Docker Engine

Install **Docker Engine**, not Docker Desktop. Docker Desktop on Linux runs containers inside a virtual machine, so USB devices (RealSense, Ultraleap), host networking and the display can't be passed through properly.

1. Follow Docker's official guide: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/). Use the **apt repository** method. It installs the Compose plugin too.
2. Let your user run Docker without `sudo` ([Linux post-install steps](https://docs.docker.com/engine/install/linux-postinstall/)):

   ```bash
   sudo usermod -aG docker $USER
   ```

   Then **log out and back in**.
3. Check it:

   ```bash
   docker run hello-world
   ```

   It should run **without** `sudo`.
4. Install VS Code and the **Dev Containers** extension (`ms-vscode-remote.remote-containers`).

---

## 2. NVIDIA GPU (skeleton node)

**The default Linux dev container needs an NVIDIA GPU.** The skeleton tracking node runs its pose model on the GPU with CUDA, so the config passes the GPU into the container with `--gpus=all`. Without an NVIDIA GPU and the toolkit below, the container will not start.

If you have an NVIDIA GPU:

1. Install the NVIDIA driver on the host (Ubuntu: **Software & Updates → Additional Drivers**), then reboot. Check with:

   ```bash
   nvidia-smi
   ```

2. Install the **NVIDIA Container Toolkit** and configure it for Docker, following NVIDIA's guide: [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). It ends with:

   ```bash
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

3. Check that Docker can see the GPU:

   ```bash
   docker run --rm --gpus all ubuntu nvidia-smi
   ```

**If you don't have an NVIDIA GPU**, you will have to edit the dev container config yourself. Remove `"--gpus=all"` from `runArgs` and `"NVIDIA_DRIVER_CAPABILITIES"` from `containerEnv` in a copy of [`.devcontainer/linux-gpu/devcontainer.json`](../.devcontainer/linux-gpu/devcontainer.json). The skeleton node will then not run, because it needs CUDA. Everything else still works.

---

## 3. Ultraleap

Ultraleap officially supports Ubuntu 22.04, but it has been tested working on 24.04 for this project.

Ultraleap no longer hosts its Linux packages, so **install from the two `.deb` files saved in the team's Teams files**. Don't follow the install commands on Ultraleap's website: they point to an apt repository that has been taken offline and will fail.

These are the exact versions used on the team's working machine:

- `ultraleap-hand-tracking-service_5.17.1.0-a9f25232-1.0_amd64.deb` (about 700 MB)
- `ultraleap-hand-tracking-control-panel_1125862.deb` (about 19 MB)

**Teams location:** the green folder called *Ultralep deb files*.

1. Download both into the same folder (for example `~/Downloads`) and install the service first, then the control panel:

   ```bash
   cd ~/Downloads
   sudo apt install ./ultraleap-hand-tracking-service_5.17.1.0-a9f25232-1.0_amd64.deb
   sudo apt install ./ultraleap-hand-tracking-control-panel_1125862.deb
   ```

   The `./` matters: it tells `apt` to install the local file instead of searching a repository. These packages are for x86_64 (amd64) only.

2. Check the install:

   ```bash
   dpkg -l | grep ultraleap
   ```

   You should see two lines starting with `ii` (service 5.17.1.0 and control panel 3.4.1).

3. Accept the licence and check the service is running:

   ```bash
   leapctl eula
   systemctl status ultraleap-hand-tracking-service
   ```

   Look for `active (running)`. If not, run `sudo systemctl start ultraleap-hand-tracking-service`.

4. Plug in the Leap Motion Controller 2 (USB 3 port).
5. Open the control panel (`ultraleap-hand-tracking-control-panel`), hold a hand 15 to 30 cm above the sensor, and confirm it draws a hand skeleton. If the control panel fails with a permissions error about a lock file in `/opt`, fix that file's permissions with `chmod` (the error names the file).
6. Confirm the SDK files the container needs exist:

   ```bash
   ls /usr/lib/ultraleap-hand-tracking-service
   ```

   You should see `libLeapC.so` in the list.

**Camera orientation matters.** The current Ultraleap software only tracks correctly when hands enter from one side of the camera. If your left and right hands come out swapped (or your right hand isn't detected at all), rotate the camera 180° on the desk, or flip the orientation in the control panel settings.

The container does **not** run the tracking service itself. The service runs on the host and the container connects to it over `localhost`, so the service must be running on the host whenever you use hand tracking.

---

## 4. RealSense

1. Plug the D455 directly into a **USB 3** port (no hub) with the supplied cable.
2. Check the link speed:

   ```bash
   lsusb -t
   ```

   The RealSense should show `5000M`. If it shows `480M` it is on USB 2: replug it firmly or try another port or cable. Many "missing stream" problems are this. Inside the container the driver logs `Device USB type: 3.x` when it is healthy; `2.1` causes dropped frames and low resolution.

3. Install the udev rules so the camera can be used without root. Download [`99-realsense-libusb.rules`](https://github.com/IntelRealSense/librealsense/blob/master/config/99-realsense-libusb.rules) from the librealsense repo (`config/` folder), then:

   ```bash
   sudo cp 99-realsense-libusb.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

   Unplug and replug the camera. If the file has moved, follow the Linux installation guide in the [librealsense repo](https://github.com/IntelRealSense/librealsense).

You don't need to install librealsense or the RealSense ROS driver on the host; the container has them. The container is privileged and mounts `/dev`, because the camera re-enumerates on the USB bus when streaming starts.

---

## 5. Graphics and display

### Render group

The container needs your machine's render group ID to use the graphics device. Run once:

```bash
echo 'export RENDER_GID=$(getent group render | cut -d: -f3)' >> ~/.profile
```

Then **log out and back in** (VS Code only sees the variable after a new login). Check it:

```bash
echo $RENDER_GID
```

It should print a number. If it prints nothing, the container still starts but falls back to software rendering, which makes Gazebo very slow.

### Display access

The container draws GUI windows (RViz, Gazebo, rqt) on your screen, which needs permission once per login. Make it automatic:

```bash
echo 'xhost +local: > /dev/null 2>&1' >> ~/.profile
```

If RViz still reports `Authorization required` after a reboot, add `xhost +local:` through the **Startup Applications** app instead, which runs after the desktop has loaded. In a pinch, just run `xhost +local:` in a host terminal.

---

## 6. Open the dev container

1. Open the repo in VS Code.
2. Command palette (Ctrl+Shift+P) → **Dev Containers: Reopen in Container**.
3. Pick **HandoverCapstone (Linux hardware)** (`.devcontainer/linux-gpu/`), or your own edited copy if you have no NVIDIA GPU ([step 2](#2-nvidia-gpu-skeleton-node)).

The first build downloads several GB and takes a while. When it finishes, the terminal prompt should start with `ubuntu@`. After any change to the Dockerfile or `devcontainer.json`, run **Dev Containers: Rebuild Container**.

---

## 7. Verify everything

Inside the container, build and source the workspace first:

```bash
colcon build
source install/setup.bash
```

| Check | Command | Expected |
|---|---|---|
| GPU (graphics) | `glxinfo -B \| grep "OpenGL renderer"` | Mentions Intel/AMD/NVIDIA, not `llvmpipe` |
| GPU (CUDA) | `python3 -c "import torch; print(torch.cuda.is_available())"` | `True` |
| GUI | `rviz2` | A window opens |
| Ultraleap bindings | `python3 -c "import leap"` | No error |
| Hand tracking | `ros2 launch handover_hand_tracking hand_tracking.launch.py` | RViz shows a hand skeleton |
| RealSense | `ros2 launch handover_realsense realsense.launch.py` | No "device not found" errors |
| RealSense image | `ros2 run rqt_image_view rqt_image_view` (pick `/camera/camera/color/image_raw`) | Live colour image |

### If the Ultraleap bindings are missing

When the container is created, it installs the Ultraleap Python bindings ([`post-create.sh`](../.devcontainer/linux-gpu/post-create.sh)). If that step failed for any reason, `import leap` fails and the hand tracking node won't run. Install them by hand inside the container:

```bash
pip install --break-system-packages cffi pycparser
pip install --break-system-packages "git+https://github.com/ultraleap/leapc-python-bindings.git#subdirectory=leapc-cffi"
pip install --break-system-packages "git+https://github.com/ultraleap/leapc-python-bindings.git#subdirectory=leapc-python-api"
python3 -c "import leap; print('leap OK')"
```

The last line should print `leap OK`. If the first `leapc-cffi` install fails with `No LeapC.h found`, the Ultraleap software is missing on the host ([step 3](#3-ultraleap)).

### Next

To run the subsystems from here, see [common_commands.md](common_commands.md) and each subsystem's code guide in the [engineering portfolio](../Engineering_Portfolio/START_HERE.md).

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Container won't start: `could not select device driver "" with capabilities: [[gpu]]` | No NVIDIA GPU, or the NVIDIA Container Toolkit isn't installed or configured. See [step 2](#2-nvidia-gpu-skeleton-node). |
| Container won't start: `bind source path does not exist: /usr/lib/ultraleap-hand-tracking-service` | Ultraleap software not installed on the host. Do [step 3](#3-ultraleap). |
| Container build fails at the pip step with `No LeapC.h found` | Same as above: the SDK folder is missing or empty on the host. |
| `docker: permission denied` | You're not in the `docker` group yet, or haven't logged out and back in ([step 1](#1-docker-engine)). |
| `Authorization required` / `could not connect to display` | Run `xhost +local:` on the host ([step 5](#display-access)). |
| RViz hangs or prints `MESA` / `failed to load driver` errors | `RENDER_GID` not set, or you didn't log out after setting it ([step 5](#render-group)). Quick workaround: `LIBGL_ALWAYS_SOFTWARE=1 rviz2`. |
| `No module named 'leap'` | The Ultraleap bindings didn't install when the container was created. See [If the Ultraleap bindings are missing](#if-the-ultraleap-bindings-are-missing). |
| Hand tracking node runs but publishes nothing | Tracking service not running on the host, or no hand in view. Check the control panel. |
| Left and right hands swapped | Camera orientation ([step 3](#3-ultraleap)). |
| `No RealSense devices were found` | udev rules missing on the host, camera not on USB 3, or replug needed ([step 4](#4-realsense)). |
| `Device USB type: 2.1` / corrupted-frame warnings | Camera is on a USB 2 link. Replug into a USB 3 port. |
| `Failed to read busnum/devnum` (HID warnings) | Usually harmless inside a container. |
| Changed `devcontainer.json` but nothing changed | Run **Dev Containers: Rebuild Container**. |

## Sources

- Docker Engine on Ubuntu: https://docs.docker.com/engine/install/ubuntu/
- NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
- librealsense (udev rules): https://github.com/IntelRealSense/librealsense
- Ultraleap Python bindings: https://github.com/ultraleap/leapc-python-bindings
