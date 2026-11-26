import cv2
import numpy as np
import random
from pathlib import Path
from ultralytics import YOLO
from grip_geometry import load_camera, pixel_to_ray, ray_to_world, ray_plane, grip_point

MODEL = "../training/runs/pose/aug2/weights/best.pt"
CAMERA_YAML = "../../handover_eye_in_hand/config/elp_ar0234_1920x1200.yaml"
IMAGE_DIR = Path("../training/datasets/screwdriver_v4/test/images")
N_IMAGES = 5

# made-up pose: camera looking straight down at the bench from 0.40 m
CAMERA_HEIGHT = 0.40
R_wc = np.array([[1, 0, 0],
                 [0, -1, 0],
                 [0, 0, -1]], dtype=float)
cam_pos = np.array([0.0, 0.0, CAMERA_HEIGHT])
plane_point = np.array([0.0, 0.0, 0.0])      # the bench top
plane_normal = np.array([0.0, 0.0, 1.0])     # up, toward the camera

R_cw = R_wc.T                                # for drawing 3D points back onto the image
t_cw = -R_cw @ cam_pos
rvec, _ = cv2.Rodrigues(R_cw)

#Run the model
K, dist = load_camera(CAMERA_YAML)
model = YOLO(MODEL)

def pixel_to_bench(u, v):
    """Pixel -> 3D point on the bench, using the made-up pose."""
    camera_pos, ray_dir = ray_to_world(pixel_to_ray(u, v, K, dist), R_wc, cam_pos)
    return ray_plane(camera_pos, ray_dir, plane_point, plane_normal)

magnet_px = int(K[0, 0] * 0.0245 / CAMERA_HEIGHT)       # 24.5 mm magnet radius, in pixels

image_paths = random.sample(sorted(IMAGE_DIR.glob("*.jpg")), N_IMAGES)
Path("real_image_results").mkdir(exist_ok=True)

for i, image_path in enumerate(image_paths, start=1):
    image = cv2.imread(str(image_path))
    result = model(image, conf=0.7, verbose=False)[0]
    classes = result.boxes.cls.cpu().numpy().astype(int)
    scores = result.boxes.conf.cpu().numpy()
    keypoints = result.keypoints.xy.cpu().numpy()
    print(f"\nimage {i}: {image_path.name[:31]}  ({len(classes)} screwdriver(s))")

    for cls, score, (handle, junction, tip) in zip(classes, scores, keypoints):
        junction_3d = pixel_to_bench(*junction)
        tip_3d = pixel_to_bench(*tip)
        pickup_point, shaft_dir, shaft_length = grip_point(junction_3d, tip_3d, plane_normal)

        uv, _ = cv2.projectPoints(pickup_point.reshape(1, 3), rvec, t_cw, K, dist)
        gx, gy = uv[0, 0]

        print(f"  {result.names[cls]} ({score:.2f}): shaft {shaft_length * 1000:.0f} mm, "
              f"pickup {pickup_point.round(3)} m")
        for x, y in (handle, junction, tip):
            cv2.circle(image, (int(x), int(y)), 8, (255, 255, 255), -1)
        cv2.circle(image, (int(gx), int(gy)), magnet_px, (0, 0, 255), 3)
        cv2.putText(image, f"{result.names[cls]} {score:.2f}", (int(junction[0]) + 15, int(junction[1]) - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    cv2.imwrite(f"real_image_results/{i}_{image_path.stem[:31]}.jpg", image)

print("\nsaved to scripts/real_image_results/")