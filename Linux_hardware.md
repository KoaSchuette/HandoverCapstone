# Linux Hardware Setup (Ultraleap + RealSense + GPU)

This guide sets up a **Linux host** to run the `Linux hardware` dev container, which
gives the container access to the Ultraleap hand tracker, the RealSense camera,
and the machine's graphics (for RViz and Gazebo).

Windows and Mac users should use the `default` config instead and can skip this.

Everything in sections 1 to 5 happens on the **host** (your normal Ubuntu
terminal), not inside the container.

> **Do section 2 before opening the container.** The `Linux hardware` config
> mounts the Ultraleap install folder from the host. If the Ultraleap software is
> not installed, the container will fail to start.

---

## 1. Docker

If Docker isn't set up yet, follow the Docker section of the main `README.md`
(Docker Engine from the apt repository, then add yourself to the `docker` group
and log out and back in). Check with:

```bash
docker run hello-world
```

It should run **without** `sudo`.

---

## 2. Ultraleap hand tracking software

Ultraleap officially supports Ubuntu 22.04, but it has been tested working on
24.04 for this project.

Ultraleap no longer hosts its Linux packages, so **install from the two `.deb`
files saved in the team's Teams files**. These are the exact versions used on the
team's working machine:

- `ultraleap-hand-tracking-service_5.17.1.0-a9f25232-1.0_amd64.deb` (about 700 MB)
- `ultraleap-hand-tracking-control-panel_1125862.deb` (about 19 MB)

Teams location: Green folder called Ultralep deb files

Download both into the same folder (for example `~/Downloads`), then install them
from that folder:

```bash
cd ~/Downloads
sudo apt install ./ultraleap-hand-tracking-service_5.17.1.0-a9f25232-1.0_amd64.deb
sudo apt install ./ultraleap-hand-tracking-control-panel_1125862.deb
```

The `./` matters: it tells `apt` to install the local file instead of searching a
repository. Install the service first, then the control panel. These packages are
for x86_64 (amd64) only.

Don't follow the install commands on Ultraleap's website: they point to an apt
repository that has been taken offline and will fail.

Check the install:

```bash
dpkg -l | grep ultraleap
```

You should see two lines starting with `ii` (service 5.17.1.0 and control panel
3.4.1). Then accept the licence and check the service is running:

```bash
leapctl eula
systemctl status ultraleap-hand-tracking-service
```

Look for `active (running)`. If not, run
`sudo systemctl start ultraleap-hand-tracking-service`.

Then:

1. Plug in the Leap Motion Controller 2 (USB 3 port).
2. Open the control panel (`ultraleap-hand-tracking-control-panel`), hold a hand
   15 to 30 cm above the sensor, and confirm it draws a hand skeleton. If the
   control panel fails with a permissions error about a lock file in `/opt`, fix
   that file's permissions with `chmod` (the error names the file).
3. Confirm the SDK files the container needs exist:

```bash
ls /usr/lib/ultraleap-hand-tracking-service
```

You should see `libLeapC.so` in the list.

**Camera orientation matters.** The current Ultraleap software only tracks
correctly when hands enter from one side of the camera. If your left and right
hands come out swapped (or your right hand isn't detected at all), rotate the
camera 180° on the desk, or flip the orientation in the control panel settings.

The container does **not** run the tracking service itself. The service runs on
the host and the container connects to it over `localhost`, so the service must be
running on the host whenever you use hand tracking.

---

## 3. Graphics access (render group)

The container needs your machine's render group ID to use the graphics device.
This works with integrated graphics; no dedicated GPU is required. Run once:

```bash
echo 'export RENDER_GID=$(getent group render | cut -d: -f3)' >> ~/.profile
```

Then **log out and back in** (VS Code only sees the variable after a new login).
Check it:

```bash
echo $RENDER_GID
```

It should print a number. If it prints nothing, the container still starts but
falls back to software rendering, which makes Gazebo very slow.

---

## 4. Display access

The container draws GUI windows (RViz, Gazebo, rqt) on your screen, which needs
permission once per login. Make it automatic:

```bash
echo 'xhost +local: > /dev/null 2>&1' >> ~/.profile
```

If RViz still reports `Authorization required` after a reboot, add `xhost +local:`
through the **Startup Applications** app instead, which runs after the desktop has
loaded. In a pinch, just run `xhost +local:` in a host terminal.

---

## 5. RealSense udev rules

Follow the **RealSense D455** section of the main `README.md` (USB 3 port, udev
rules, replug the camera).

---

## 6. Open the dev container

1. Open the repo in VS Code.
2. Command palette (Ctrl+Shift+P) → **Dev Containers: Reopen in Container**.
3. Pick **HandoverCapstone (Linux hardware)**.

The first build downloads several GB and takes a while. When it finishes, the
terminal prompt should start with `ubuntu@`.

---

## 7. Verify everything

Inside the container, build and source the workspace first:

```bash
colcon build
source install/setup.bash
```

| Check | Command | Expected |
|---|---|---|
| GPU | `glxinfo -B \| grep "OpenGL renderer"` | Mentions Intel/AMD/NVIDIA, not `llvmpipe` |
| GUI | `rviz2` | A window opens |
| Ultraleap bindings | `python3 -c "import leap"` | No error |
| Hand tracking | `ros2 launch handover_hand_tracking hand_tracking.launch.py` | RViz shows a hand skeleton |
| RealSense | `ros2 launch handover_realsense realsense.launch.py` | No "device not found" errors |

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Container won't start: `bind source path does not exist: /usr/lib/ultraleap-hand-tracking-service` | Ultraleap software not installed on the host. Do section 2. |
| Container build fails at the pip step with `No LeapC.h found` | Same as above: the SDK folder is missing or empty on the host. |
| `Authorization required` / `could not connect to display` | Run `xhost +local:` on the host (section 4). |
| RViz hangs or prints `MESA` / `failed to load driver` errors | `RENDER_GID` not set, or you didn't log out after setting it (section 3). Quick workaround: `LIBGL_ALWAYS_SOFTWARE=1 rviz2`. |
| Hand tracking node runs but publishes nothing | Tracking service not running on the host, or no hand in view. Check the control panel. |
| Left and right hands swapped | Camera orientation (see section 2). |
| `No RealSense devices were found` | udev rules missing on the host, camera not on USB 3, or replug needed. |
| Changed `devcontainer.json` but nothing changed | Run **Dev Containers: Rebuild Container**. |

## Sources

- Ultraleap Python bindings: https://github.com/ultraleap/leapc-python-bindings