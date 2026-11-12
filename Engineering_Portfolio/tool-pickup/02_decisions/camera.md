# Camera

## Decision

Use an ELP AR0234 global-shutter USB camera (ELP-USBGS1200P01-H110, $122.97) as the eye-in-hand camera on the robot's wrist. Specced by Ryan Donen and Koa Schuette, calibrated by Tanner Warren.

## Context

The proposal planned a RealSense D435 on the wrist, provided by Ingenuity Labs. When asked on Oct 20, Dr. Pan said the lab had no spare D435, so the team needed to buy a camera. Requirements from the team's vendor comparison: global shutter, USB, colour.

## Options considered

| Option | For | Against |
|---|---|---|
| RealSense D435 | Colour + depth in one camera; matched the proposal | None available in the lab |
| Arducam AR0234 USB 3.0 (B0495C) | Same sensor as the ELP | $221, close to half the project budget |
| Arducam OV9782 (B0385) | Cheaper | 70° field of view (too narrow at close range); lower resolution |
| **ELP AR0234, 110° lens** (chosen) | Global shutter; wide field of view; $122.97 | Colour only, no depth |

## Why global shutter

A rolling-shutter camera reads the image one row at a time, so anything moving while the frame is captured comes out skewed. A global shutter exposes the whole frame at once. The camera rides on the arm, so the camera itself is often the thing moving, and a skewed image would shift the detected tool position.

## Consequence: no depth

The proposal located tools using a depth camera. The ELP has no depth, so a pixel only gives a *direction* from the camera, not a distance. The plan instead is to intersect that direction with the board's plane, which is known from the CAD and the datum check (see the tool rack's [fixed position](../../tool-rack/02_decisions/fixed-position.md) decision). This only works because the board doesn't move, and it needs an accurate hand-eye calibration.

## Verification

The [intrinsic calibration](../06_experiments/intrinsic-calibration/) checked the camera against its listing:

| | Listing | Measured |
|---|---|---|
| Field of view | "110°", "no distortion" | 107° horizontal, 115° diagonal |
| Distortion | none | Moderate barrel distortion: about 20 px shift 600 px from the centre, 100 px at the left/right edges, 155 px in the corners |

The field of view roughly matches the "110°" name. The "no distortion" claim doesn't hold, so the calibrated distortion model has to be applied before any measurement.

## Looking back

Losing depth moved work from the camera onto calibration and geometry: tool positions now depend on the hand-eye calibration and on the board staying where the CAD says it is. That consequence wasn't written down when the camera was chosen. Recording it at the time would have flagged hand-eye calibration as a critical step much earlier.