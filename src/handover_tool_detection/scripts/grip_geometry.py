import numpy as np
import cv2
import yaml

def load_camera(yaml_path):
    """Read K (3x3) and the distortion coefficients from a ROS camera_info YAML."""
    with open(yaml_path) as f:
        cal = yaml.safe_load(f)

    K = np.array(cal["camera_matrix"]["data"]).reshape(3, 3)
    dist = np.array(cal["distortion_coefficients"]["data"])
    return K, dist

def pixel_to_ray(u, v, K, dist):
    """Unit direction (camera frame) of the light that hit pixel (u, v)."""
    pts = np.array([[[u, v]]], dtype=np.float64)
    x, y = cv2.undistortPoints(pts, K, dist)[0, 0]
    ray = np.array([x, y, 1.0])
    return ray / np.linalg.norm(ray)

def ray_to_world(ray_cam, R_wc, cam_pose):
    """Turn a camera-frame ray into a world-frame ray starting at the camera."""
    camera_pos = np.asarray(cam_pose, dtype=float)
    ray_dir = R_wc @ ray_cam   # rotate the direction into world axes
    return camera_pos, ray_dir


def ray_plane(camera_pos, ray_dir, plane_point, plane_normal):
    """Where the ray from the camera hits the plane (bench or pegboard)"""
    to_plane = -np.asarray(plane_normal, dtype=float)
    d = (np.asarray(plane_point, dtype=float) - camera_pos) @ to_plane
    cos_angle = ray_dir @ to_plane
    if d <= 0 or cos_angle <= 1e-6:
        return None

    hyp = d / cos_angle
    return camera_pos + hyp * ray_dir

def grip_point(junction, tip, normal, grip_from_junction=0.050, shaft_radius=0.0032):
    """Where the magnet touches the shaft, and which way the shaft points (handle -> tip)."""
    junction = np.asarray(junction, dtype=float)
    tip = np.asarray(tip, dtype=float)

    shaft = tip - junction
    shaft_length = np.linalg.norm(shaft)
    shaft_dir = shaft / shaft_length

    on_centreline = junction + grip_from_junction * shaft_dir
    pickup_point = on_centreline + shaft_radius * np.asarray(normal, dtype=float)

    return pickup_point, shaft_dir, shaft_length

