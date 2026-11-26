import time
import cv2
import numpy as np
from ultralytics import YOLO
from grip_geometry import load_camera, pixel_to_ray, ray_to_world, ray_plane, grip_point
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent      # .../handover_tool_detection/scripts
MODEL = str(HERE.parent / "training" / "best.pt")
CAMERA_YAML = HERE.parents[1] / "handover_eye_in_hand" / "config" / "elp_ar0234_1920x1200.yaml"
sys.path.append(str(HERE.parents[1] / "handover_eye_in_hand" / "calibration"))
from elp_camera import open_camera

CAMERA_INDEX = 0      
CAMERA_HEIGHT = 0.45    # MEASURE lens to bench, in metres
CONF = 0.7

R_wc = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=float)   # straight down
cam_pos = np.array([0.0, 0.0, CAMERA_HEIGHT])
plane_point = np.array([0.0, 0.0, 0.0])                              # bench top
plane_normal = np.array([0.0, 0.0, 1.0])                             # up
R_cw = R_wc.T
t_cw = -R_cw @ cam_pos
rvec, _ = cv2.Rodrigues(R_cw)

K, dist = load_camera(CAMERA_YAML)
magnet_px = int(K[0, 0] * 0.0245 / CAMERA_HEIGHT)                    # 24.5 mm magnet radius in pixels


def pixel_to_bench(u, v):
    camera_pos, ray_dir = ray_to_world(pixel_to_ray(u, v, K, dist), R_wc, cam_pos)
    return ray_plane(camera_pos, ray_dir, plane_point, plane_normal)

def draw_pickup(view, junction, tip):
    """Run the geometry for one tool and draw the magnet circle on the image."""
    junction_3d = pixel_to_bench(*junction)
    tip_3d = pixel_to_bench(*tip)
    if junction_3d is None or tip_3d is None:
        return
    pickup_point, shaft_dir, shaft_length = grip_point(junction_3d, tip_3d, plane_normal)
    uv, _ = cv2.projectPoints(pickup_point.reshape(1, 3), rvec, t_cw, K, dist)
    gx, gy = int(uv[0, 0][0]), int(uv[0, 0][1])
    cv2.circle(view, (gx, gy), magnet_px, (0, 0, 255), 4)
    cv2.drawMarker(view, (gx, gy), (0, 0, 255), cv2.MARKER_CROSS, 30, 3)
    cv2.putText(view, f"pickup  shaft {shaft_length * 1000:.0f} mm", (gx + magnet_px + 10, gy),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

if __name__ == "__main__":
    model = YOLO(MODEL)
    cap = open_camera(CAMERA_INDEX, 1920, 1200, 30, "MJPG")
    if cap is None:
        raise SystemExit("Could not open the camera. Run elp_camera.py --list to find the index.")
    ok, frame = cap.read()
    if not ok or frame.shape[:2] != (1200, 1920):
        raise SystemExit("Camera did not give 1920x1200. The calibration only fits that size.")
    print("running: q = quit, s = save snapshot")
    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        start = time.time()
        result = model(frame, conf=CONF, verbose=False)[0]
        view = result.plot()                          # boxes, keypoints, colour + confidence
        for junction, tip in result.keypoints.xy.cpu().numpy()[:, 1:3]:
            draw_pickup(view, junction, tip)
        fps = 1.0 / (time.time() - start)
        cv2.putText(view, f"{fps:.1f} fps   assumed height {CAMERA_HEIGHT:.2f} m", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
        cv2.imshow("screwdriver detection", cv2.resize(view, (960, 600)))
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord("s"):
            name = f"live_{time.strftime('%H%M%S')}.jpg"
            cv2.imwrite(name, view)
            print("saved", name)
    cap.release()
    cv2.destroyAllWindows()