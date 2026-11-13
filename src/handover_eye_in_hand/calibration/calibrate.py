#!/usr/bin/env python3
"""Calibrate the ELP camera from chessboard snapshots in images/."""
import glob, cv2, yaml
import numpy as np

COLS, ROWS = 9, 6
SQUARE = 0.020

#corner pose
objp = np.zeros((COLS*ROWS, 3), np.float32)
i = 0
for r in range(ROWS):
    for c in range(COLS):
        objp[i] = (c * SQUARE, r * SQUARE, 0.0)
        i += 1

files = sorted(glob.glob("images/*.png"))
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

obj_points, img_points, used = [], [], []
for f in files:
    gray = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, (COLS, ROWS))
    if not found:
        print(f"MISSED  {f}")
        continue

    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    obj_points.append(objp)
    img_points.append(corners)
    used.append(f)
    print(f"ok      {f}")

print(f"\n{len(img_points)} of {len(files)} images usable, size {gray.shape[::-1]}")

#calibration
rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)
np.set_printoptions(precision=4, suppress=True)

print(f"\nRMS reprojection error: {rms:.3f} px")
print("K =\n", K)
print("dist (k1 k2 p1 p2 k3) =", dist.ravel())

print("\nper-image:   error   distance   file")
for f, op, ip, rv, tv in zip(used, obj_points, img_points, rvecs, tvecs):
    proj, _ = cv2.projectPoints(op, rv, tv, K, dist)
    err = np.sqrt(np.mean(np.sum((ip - proj) ** 2, axis=2)))
    print(f"           {err:5.2f} px  {tv[2][0]:5.2f} m   {f}")

allc = np.vstack(img_points).reshape(-1, 2)
print(f"\ncorners reached x {allc[:,0].min():.0f}-{allc[:,0].max():.0f} of 1920, "
      f"y {allc[:,1].min():.0f}-{allc[:,1].max():.0f} of 1200")

#Corrected images
h, w = gray.shape
info = {
    "image_width": w,
    "image_height": h,
    "camera_name": "elp_eye_in_hand",
    "camera_matrix": {"rows": 3, "cols": 3, "data": K.flatten().tolist()},
    "distortion_model": "plumb_bob",
    "distortion_coefficients": {"rows": 1, "cols": 5, "data": dist.flatten().tolist()},
    "rectification_matrix": {"rows": 3, "cols": 3, "data": np.eye(3).flatten().tolist()},
    "projection_matrix": {"rows": 3, "cols": 4,
                          "data": np.hstack([K, np.zeros((3, 1))]).flatten().tolist()},
}
out = "../config/elp_ar0234_1920x1200.yaml"
with open(out, "w") as f:
    yaml.safe_dump(info, f, sort_keys=False)
print(f"\nsaved {out}")

test = cv2.imread(used[0])         # swap in a file where the board is near an edge
new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist, (w, h), 1, (w, h))
und = cv2.undistort(test, K, dist, None, new_K)
cv2.imwrite("undistorted_check.png", np.hstack([test, und]))
print("wrote undistorted_check.png (left = original, right = corrected)")