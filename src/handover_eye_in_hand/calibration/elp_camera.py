#!/usr/bin/env python3
"""
Capture and display live video from an ELP USB (UVC) camera using OpenCV.

Install:   pip install opencv-python
Run:       python elp_camera.py                      # camera 0, 1280x720 @ 30 fps
           python elp_camera.py -c 1 -W 1920 -H 1080 --fps 30
           python elp_camera.py --list               # find available camera indices

Keys while running:
    q or ESC  quit
    s         save a snapshot (PNG)
    r         start/stop recording (AVI, MJPG)
"""

import argparse
import platform
import sys
import time
from datetime import datetime

import cv2


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


def main():
    p = argparse.ArgumentParser(description="Display video from an ELP USB camera.")
    p.add_argument("-c", "--camera", type=int, default=0, help="camera index (default 0)")
    p.add_argument("-W", "--width", type=int, default=1280)
    p.add_argument("-H", "--height", type=int, default=720)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--fourcc", default="MJPG",
                   help="pixel format: MJPG (default) or YUY2; use '' to leave unchanged")
    p.add_argument("--list", action="store_true", help="list available cameras and exit")
    args = p.parse_args()

    if args.list:
        list_cameras()
        return 0

    cap = open_camera(args.camera, args.width, args.height, args.fps, args.fourcc)
    if cap is None:
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

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS) or args.fps
    print(f"Camera {args.camera} opened: {actual_w}x{actual_h} @ {actual_fps:.0f} fps (requested)")
    print("Keys: q/ESC = quit, s = snapshot, r = record on/off")

    window = "ELP Camera"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    writer = None
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

            # Measure real frame rate, updated about once per second.
            frame_count += 1
            now = time.time()
            if now - t_last >= 1.0:
                fps_display = frame_count / (now - t_last)
                frame_count = 0
                t_last = now

            if writer is not None:
                writer.write(frame)

            shown = frame.copy()
            label = f"{shown.shape[1]}x{shown.shape[0]}  {fps_display:.1f} fps"
            if writer is not None:
                label += "  [REC]"
            cv2.putText(shown, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 0, 255) if writer is not None else (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(window, shown)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("s"):
                name = datetime.now().strftime("snapshot_%Y%m%d_%H%M%S_%f.png")
                cv2.imwrite(name, frame)
                print(f"Saved {name}")
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