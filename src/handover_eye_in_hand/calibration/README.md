# ELP eye-in-hand camera: intrinsic calibration

Camera: ELP-USBGS1200P01 (AR0234, global shutter, fixed focus), used at **1920×1200, MJPG**.
Result: `../config/elp_ar0234_1920x1200.yaml` (ROS camera_info format, plumb_bob model).

## Result (8 Nov 2026, 31 images)
- fx 716.5, fy 715.0, cx 959.7, cy 524.4 px
- RMS reprojection error 0.68 px (≈0.3 mm at 0.3 m)
- The lens is wider than the product page says: ~107° horizontal FOV, moderate barrel distortion (~100 px at the image edges)

## The calibration is only valid if
- The camera runs at **1920×1200** (other resolutions need their own calibration)
- **Nobody twists or bumps the lens.** If that happens, recalibrate

## How to recalibrate
1. Print `chessboard_10x7_20mm_letter.pdf` at 100% (10×7 squares of 20 mm → pattern size (9, 6)) and tape it flat to a wall.
2. Capture in Windows PowerShell (USB cameras don't reach WSL/Docker). Press `s` for a snapshot. Take 25–30 at 0.25–0.45 m: tilted, in every corner and edge of the image, whole board visible.
3. Run in the container, from `calibration/`: `python3 calibrate.py`
4. Check that RMS is under ~1 px and that the corners cover most of the image, then commit the new YAML.

`images/` is git-ignored. Keep the photos on the shared Drive if needed.