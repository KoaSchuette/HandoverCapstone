#!/usr/bin/env python3
"""
Capture and display live video from an ELP USB (UVC) camera using OpenCV.

Install:   pip install opencv-python
Run:       python elp_camera.py                      # camera 0, 1280x720 @ 30 fps
           python elp_camera.py -c 1 -W 1920 -H 1080 --fps 30
           python elp_camera.py --list               # find available camera indices
           python elp_camera.py -W 1920 -H 1200 --calib calib.npz   # undistort saved images

--calib FILE: undistort snapshots/recordings before saving, using the camera
matrix and distortion coefficients in FILE: a ROS camera_info .yaml (e.g.
elp_robot_calibio.yaml), or .npz / .json / OpenCV .yml/.xml with keys
camera_matrix/K/mtx, dist_coeffs/D/dist and optional image_size [w, h].
The live preview stays raw. Without --calib nothing changes.

--autocapture: start with autocapture already on (a snapshot every second).
Press v at any time to turn it on or off.

Keys while running:
    q or ESC  quit
    s         save a snapshot (PNG)
    v         start/stop autocapture (one snapshot per second)
    r         start/stop recording (AVI, MJPG)
"""

import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime

import cv2
import numpy as np

AUTOCAPTURE_INTERVAL = 1.0   # seconds between automatic snapshots


def pick_backend():
    system = platform.system()
    if system == "Windows":
        return cv2.CAP_DSHOW      # faster startup and better control than MSMF
    if system == "Linux":
        return cv2.CAP_V4L2
    if system == "Darwin":
        return cv2.CAP_AVFOUNDATION
    return cv2.CAP_ANY


def list_cameras(max_index=10):
    backend = pick_backend()
    found = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i, backend)
        if cap.isOpened():
            ok, _ = cap.read()
            if ok:
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                found.append((i, w, h))
        cap.release()
    if found:
        print("Available cameras:")
        for i, w, h in found:
            print(f"  index {i}: {w}x{h}")
    else:
        print("No cameras found.")


def try_open(index, backend, width, height, fps, fourcc):
    """Open the camera with the given settings and confirm it really delivers frames."""
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        cap.release()
        return None

    # Set the pixel format FIRST. Most ELP cameras only reach high resolution /
    # frame rates over MJPG; the default YUY2 is limited by USB bandwidth.
    if fourcc:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
    if width and height:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if fps:
        cap.set(cv2.CAP_PROP_FPS, fps)

    # Warm-up: many cameras return empty frames for the first second or so.
    for _ in range(40):
        ok, frame = cap.read()
        if ok and frame is not None:
            return cap
        time.sleep(0.05)

    cap.release()
    return None


def open_camera(index, width, height, fps, fourcc):
    """Try the requested settings, then progressively safer fallbacks."""
    primary = pick_backend()
    backends = [primary] + [b for b in (cv2.CAP_ANY,) if b != primary]
    attempts = [
        (width, height, fps, fourcc),      # what you asked for
        (width, height, fps, ""),          # same, but camera's default format
        (640, 480, 30, "MJPG"),            # safe MJPG mode
        (640, 480, 30, ""),                # safest: 640x480, default format
        (0, 0, 0, ""),                     # leave everything to the driver
    ]
    for backend in backends:
        for w, h, f, fc in attempts:
            cap = try_open(index, backend, w, h, f, fc)
            if cap is not None:
                print(f"Opened with backend={backend}, requested "
                      f"{w}x{h} @ {f} fps, format={fc or 'default'}")
                return cap
    return None


def _pick(data, names):
    for name in names:
        if name in data and data[name] is not None:
            return np.asarray(data[name], dtype=np.float64)
    return None


def _floats(s):
    return [float(v) for v in s.strip().strip("[]").split(",") if v.strip()]


def _parse_ros_yaml(text):
    """Minimal parser for ROS camera_info YAML (no PyYAML needed)."""
    root, section, list_key = {}, None, None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        s = line.strip()
        if not s:
            continue
        if s.startswith("-"):
            if section is not None and list_key:
                section[list_key].append(float(s[1:].strip()))
            continue
        key, _, val = s.partition(":")
        val = val.strip()
        if len(line) == len(line.lstrip()):          # top-level key
            section, list_key = None, None
            if val.startswith("["):
                root[key] = _floats(val)
            elif val:
                root[key] = val
            else:
                section = root[key] = {}
        elif section is not None:                    # key inside a block
            if val.startswith("["):
                section[key] = _floats(val)
            elif val:
                section[key] = val
            else:
                section[key] = []
                list_key = key
    return root


def _ros_calibration(root):
    """Turn parsed ROS camera_info into the keys load_calibration expects."""
    def arr(*names):
        for n in names:
            v = root.get(n)
            if isinstance(v, dict):
                v = v.get("data")
            if v:
                return v
        return None

    model = root.get("distortion_model", "plumb_bob")
    if model not in ("plumb_bob", "rational_polynomial"):
        raise ValueError(f"Unsupported distortion model '{model}' "
                         "(supported: plumb_bob, rational_polynomial).")
    data = {"camera_matrix": arr("camera_matrix", "K"),
            "dist_coeffs": arr("distortion_coefficients", "D")}
    w = root.get("image_width", root.get("width"))
    h = root.get("image_height", root.get("height"))
    if w and h:
        data["image_size"] = [int(w), int(h)]
    return data


def load_calibration(path):
    """Return (K, D, image_size or None) from a ROS camera_info .yaml, .npz, .json or OpenCV .yml/.xml."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".npz":
        data = dict(np.load(path))
    elif ext == ".json":
        with open(path) as f:
            data = {k: np.array(v) for k, v in json.load(f).items()}
    else:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if ext in (".yml", ".yaml") and not text.lstrip().startswith("%YAML"):
            data = _ros_calibration(_parse_ros_yaml(text))   # ROS camera_info format
        else:
            fs = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)
            if not fs.isOpened():
                raise ValueError(f"Could not open calibration file {path}")
            data = {key: fs.getNode(key).mat() for key in fs.root().keys()}
            fs.release()

    K = _pick(data, ("camera_matrix", "K", "mtx"))
    D = _pick(data, ("dist_coeffs", "D", "dist"))
    if K is None or D is None:
        raise ValueError("Calibration file needs a camera matrix (camera_matrix/K/mtx) "
                         "and distortion coefficients (dist_coeffs/D/dist).")
    size = _pick(data, ("image_size",))
    if size is not None:
        size = tuple(int(v) for v in size.reshape(-1)[:2])
    return K.reshape(3, 3), D.reshape(-1), size


def main():
    p = argparse.ArgumentParser(description="Display video from an ELP USB camera.")
    p.add_argument("-c", "--camera", type=int, default=0, help="camera index (default 0)")
    p.add_argument("-W", "--width", type=int, default=1920)
    p.add_argument("-H", "--height", type=int, default=1200)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--fourcc", default="MJPG",
                   help="pixel format: MJPG (default) or YUY2; use '' to leave unchanged")
    p.add_argument("--list", action="store_true", help="list available cameras and exit")
    p.add_argument("--calib", metavar="FILE",
                   help="calibration file; saved images are undistorted with it")
    p.add_argument("--autocapture", action="store_true",
                   help="start with autocapture on (a snapshot every second); toggle with v")
    args = p.parse_args()

    if args.list:
        list_cameras()
        return 0

    cap = open_camera(args.camera, args.width, args.height, args.fps, args.fourcc)
    if cap is None:
        print(f"Could not open camera {args.camera}. Try --list, another index, "
              "or check that no other app is using the camera.", file=sys.stderr)
        return 1
    ok, first = cap.read()

    if not ok or first is None:
        print("Camera opened but gave no frame.", file=sys.stderr)
        return 1
    h, w = first.shape[:2]
    if (w, h) != (args.width, args.height):
        print(f"Camera gave {w}x{h}, not the {args.width}x{args.height} requested. "
              "Not safe for calibration - stopping.", file=sys.stderr)
        cap.release()
        return 1

    # Optional: precompute undistortion maps from the calibration file.
    map1 = map2 = None
    if args.calib:
        try:
            K, D, calib_size = load_calibration(args.calib)
            if calib_size is not None and calib_size != (w, h):
                raise ValueError(f"Calibration was made at {calib_size[0]}x{calib_size[1]} "
                                 f"but the camera is running at {w}x{h}.")
            map1, map2 = cv2.initUndistortRectifyMap(K, D, None, K, (w, h), cv2.CV_16SC2)
        except Exception as e:
            print(f"Calibration error: {e}", file=sys.stderr)
            cap.release()
            return 1
        print(f"Calibration loaded from {args.calib}; saved images will be undistorted.")

    def to_save(img):
        """Frame as it should be saved: undistorted if a calibration was given
        (done on the raw, unrotated image the calibration belongs to), then
        rotated 180 degrees to match the preview."""
        if map1 is not None:
            img = cv2.remap(img, map1, map2, cv2.INTER_LINEAR)
        return cv2.rotate(img, cv2.ROTATE_180)

    def save_snapshot(img):
        name = datetime.now().strftime("snapshot_%Y%m%d_%H%M%S_%f.png")
        cv2.imwrite(name, to_save(img))
        print(f"Saved {name}")

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS) or args.fps
    print(f"Camera {args.camera} opened: {actual_w}x{actual_h} @ {actual_fps:.0f} fps (requested)")
    print("Keys: q/ESC = quit, s = snapshot, v = autocapture on/off, r = record on/off")

    window = "ELP Camera"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    writer = None
    autocapture = args.autocapture
    next_auto = time.monotonic()
    if autocapture:
        print(f"Autocapture ON: one snapshot every {AUTOCAPTURE_INTERVAL:g} s (v to stop)")
    failures = 0
    reopens = 0
    frame_count = 0
    fps_display = 0.0
    t_last = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                # Dropped frames are normal on USB cameras (bandwidth, power,
                # corrupt MJPG frames). Skip them, and if the stream stalls for
                # ~1.5 s, close and reopen the camera instead of exiting.
                failures += 1
                if failures >= 50:
                    reopens += 1
                    if reopens > 5:
                        print("Camera could not be recovered. Check the cable, "
                              "USB port/hub and power.", file=sys.stderr)
                        break
                    print(f"Stream stalled - reopening camera (attempt {reopens}/5)...",
                          file=sys.stderr)
                    cap.release()
                    time.sleep(1.0)
                    cap = open_camera(args.camera, args.width, args.height,
                                      args.fps, args.fourcc)
                    if cap is None:
                        print("Camera did not come back.", file=sys.stderr)
                        break
                    failures = 0
                elif cv2.waitKey(30) & 0xFF in (ord("q"), 27):
                    break
                continue
            failures = 0
            reopens = 0

            if map1 is not None and frame.shape[:2] != map1.shape[:2]:
                print(f"Frame size changed to {frame.shape[1]}x{frame.shape[0]}; the "
                      "calibration no longer applies. Stopping.", file=sys.stderr)
                break

            # Autocapture: save one snapshot every AUTOCAPTURE_INTERVAL seconds.
            if autocapture:
                t = time.monotonic()
                if t >= next_auto:
                    save_snapshot(frame)
                    next_auto += AUTOCAPTURE_INTERVAL
                    if next_auto < t:            # fell behind (slow save): don't burst
                        next_auto = t + AUTOCAPTURE_INTERVAL

            # Measure real frame rate, updated about once per second.
            frame_count += 1
            now = time.time()
            if now - t_last >= 1.0:
                fps_display = frame_count / (now - t_last)
                frame_count = 0
                t_last = now

            if writer is not None:
                writer.write(to_save(frame))

            shown = cv2.rotate(frame.copy(), cv2.ROTATE_180)
            label = f"{shown.shape[1]}x{shown.shape[0]}  {fps_display:.1f} fps"
            if autocapture:
                label += "  [AUTO]"
            if writer is not None:
                label += "  [REC]"
            cv2.putText(shown, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 0, 255) if writer is not None else (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(window, shown)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("s"):
                save_snapshot(frame)
            if key == ord("v"):
                autocapture = not autocapture
                if autocapture:
                    next_auto = time.monotonic()      # first photo right away
                    print(f"Autocapture ON: one snapshot every {AUTOCAPTURE_INTERVAL:g} s")
                else:
                    print("Autocapture OFF")
            if key == ord("r"):
                if writer is None:
                    name = datetime.now().strftime("recording_%Y%m%d_%H%M%S.avi")
                    h, w = frame.shape[:2]
                    writer = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*"MJPG"),
                                             actual_fps if actual_fps > 1 else 30, (w, h))
                    print(f"Recording to {name}")
                else:
                    writer.release()
                    writer = None
                    print("Recording stopped")

            # Window closed with the X button
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        if writer is not None:
            writer.release()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())