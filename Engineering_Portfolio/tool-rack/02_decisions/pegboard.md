# Pegboard

## Decision

Use a standard 1/4" hardboard pegboard, cut to 400 × 300 mm, with 3D-printed hooks to hold the three screwdrivers, rather than a custom-built rack.

## Context

The rack has to hold three tools at fixed, repeatable positions, with each tool's steel end exposed so the electromagnet can pick it up. It also has to fit inside a $500 project budget shared with the end effector and the camera.

## Options considered

| Option | For | Against |
|---|---|---|
| Custom rack (3D printed or machined) | Exact slot shape for each tool | $200 budgeted in the proposal; slot positions are fixed once made |
| IKEA Skådis pegboard | Cheap, modular, ready-made hooks | No IKEA close, shipping costs were big and shipping time was long |
| **Hardboard pegboard + printed hooks** (chosen) | $13.77; slots can move on the hole grid without new parts; flat face gives a clean reference plane for the datum check | Hardboard can flex; hooks can wobble in the holes, which affects repeatability |

## Why

At $13.77, this allows for the rest of the $200 budgeted for the frame. The hole grid means a slot can move without making new parts, which matters while the tool layout is still being tuned for the camera. Printing the hooks lets us shape them so each tool hangs with its steel end where the magnet expects it.

## How it will be verified

The tool has to hang in the same place every time, closely enough that the magnet still grabs it on a fixed approach. Hang and remove each tool [TBD: number] times and measure how much the steel end moves. Compare that with the misalignment the electromagnet tolerates [TBD: from end-effector testing].

## Looking back

The board was chosen early, but the hooks, which actually decide where and how each tool hangs, still haven't been designed. The hook shape sets the pickup pose, so it should have been designed alongside the board rather than after it.
