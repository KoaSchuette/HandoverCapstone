# Pegboard

## Decision

Use a 3/16” perforated hardboard panel, cut to 400 × 300 mm, with 3D-printed hooks to hold the three screwdrivers, rather than a custom-built rack.

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

## Planned verification

The electromagnet face has a 25 mm radius, so the steel end can’t sit more than about 25 mm minus half its own width off-centre and still be under the face. The real limit is likely smaller, because holding force drops when the steel doesn’t bridge the magnet’s centre and outer poles. Two tests are planned for after the rack and end effector are built. First, measure the lateral offset and gap at which the electromagnet still holds a screwdriver. Second, hang and remove each tool 10 times, measuring the steel end’s position against a reference mark on the board with calipers. The hooks pass if the spread from the second test stays inside the tolerance from the first.

## Looking back

The board was chosen early, but the hooks, which actually decide where and how each tool hangs, still haven't been designed. The hook shape sets the pickup pose, so it should have been designed alongside the board rather than after it.
