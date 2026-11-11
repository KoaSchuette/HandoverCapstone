# Fixed position

## Decision

The robot knows where the board is from the CAD model (the `pegboard_face` frame in `handover_cell`). After assembly, a one-time datum check confirms it. No fiducial markers are used to locate the board.

## Context

The team’s September spec (Tool Handoff Spec, Sep 24) located the board with ArUco markers so it could be moved without reprogramming. The October proposal dropped the markers. located the board with ArUco markers, so it could be moved without reprogramming. The October proposal dropped the markers.

## Options considered

| Option | For | Against |
|---|---|---|
| ArUco markers on the board | Board can move freely; the robot finds it each time | Adds a detection step that can fail; the camera must see the markers; marker pose error grows with distance |
| CAD position only | Simplest | Build error goes unchecked |
| **CAD position + datum check** (chosen) | No vision needed to locate the board; build error is caught once | Any move means redoing the check and updating the model |

## Why

The board and the robot are both mounted on the same cart, so their relative position doesn't change during operation. Tracking something that never moves adds a failure point without adding information. Removing it leaves the camera with one job: telling which tool is in which slot.

## The datum check

From the proposal (section 6.1): guide a datum tool on the end effector to three corners of the board and record each position. Three points fix the board's plane, position and rotation in the robot's base frame. Compare the result with `pegboard_face` and update the model if they differ by more than the pickup can tolerate. That limit will come from the planned end-effector tolerance test (see pegboard).

Status: not built yet.

## Looking back

This decision is in tension with [adjustable arms](adjustable-arms.md). We removed the feature that made moving the board cheap, then decided to make the board movable. That trade still holds, because adjustments only happen during setup and never in operation, but every adjustment now costs a datum check and a model update. We should have weighed the two decisions together rather than a month apart.
