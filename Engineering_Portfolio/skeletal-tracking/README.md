# Skeletal tracking: start here

> **Owner:** Koa · **Status:** early. One pose model (YOLO26n-pose) has been tested with the RealSense D455. No model has been chosen yet, so there is no decision record. · **Reviewed against:** commit `d3010c3` (2026-11-12)

The skeletal tracking subsystem is for **safety**. It finds people's bodies in the RealSense camera image and gives the 3D position of each joint (head, shoulders, elbows, wrists and so on), so the system can tell when a person's body is in the arm's way. For example, if someone's head enters the cell, the robot stops its motion.

**How the safety check will work is not decided yet.** Which body parts count, what zone around the arm or cell triggers a stop, and whether the robot stops or slows are all still open. This page describes the general idea and what has been built so far.

To run it, see [`05_code/`](05_code/how-to-run.md).

**Videos:**

- [YOLO26n-pose skeleton tracking test](07_data/Screencast%20from%202026-10-11%2017-27-26.webm): YOLO26n-pose running live on the RealSense, shown in RViz

## Contents

1. [Requirements it serves](#1-requirements-it-serves)
2. [How it works now](#2-how-it-works-now)
3. [Testing so far](#3-testing-so-far)
4. [Interfaces](#4-interfaces)
5. [Future work](#5-future-work)

## 1. Requirements it serves

None of the project requirements (R1 to R7 in the [portfolio start page](../README.md)) cover operator safety yet. A safety requirement is TBD, for example: stop the arm within a set time when a body part enters a set zone.

Subsystem requirements are not written yet (TBD).

## 2. How it works now

The current node runs **YOLO26n-pose** on the RealSense colour image. It outputs the 17 COCO keypoints (nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles) and uses the RealSense depth image to give each one a 3D position in the camera frame. Keypoints it can't find are published as NaN.

## 3. Testing so far

YOLO26n-pose was run live with the RealSense and viewed in RViz (see the video above).

**What was found:** the model works in 2D only and does not use depth itself. When a body part points straight toward or away from the camera, parallel to its line of sight, the part looks very short in the image. The model then loses those keypoints or places them badly. Reading depth at a single pixel can't recover this. For safety this matters: a body part the tracker loses is one the robot can't stop for, and a person leaning or reaching toward the robot (and so toward the camera) is exactly that case.

[TBD: date, setup (camera position, operator distance), and how often keypoints were lost]

## 4. Interfaces

| Direction | Type | Name | Interface |
|---|---|---|---|
| In | Topic | `camera/camera/color/image_raw` | `sensor_msgs/Image` |
| In | Topic | `camera/camera/aligned_depth_to_color/image_raw` | `sensor_msgs/Image` (depth in mm) |
| In | Topic | `camera/camera/color/camera_info` | `sensor_msgs/CameraInfo` (intrinsics, read once) |
| Out | Topic | `skeleton/position` | `handover_interfaces/Skeleton`: 17 keypoints (m, camera colour frame) and 17 confidences |
| Out | Topic | `/skeleton/markers` | `visualization_msgs/MarkerArray` for RViz |

Nothing uses `skeleton/position` yet, and nothing stops the robot from it ([system start page](../system/README.md)).

## 5. Future work

- **Test other pose models and compare their accuracy with YOLO26n-pose**, especially on body parts pointing toward the camera. The next model to try is [TBD: model name].
