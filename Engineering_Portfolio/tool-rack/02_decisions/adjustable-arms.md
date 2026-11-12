# Adjustable arms, starting at 35 cm

## Decision

Leave the two frame arms that connect the pegboard uprights to the cart uncut and longer than needed, and clamp the uprights along them so the board can slide toward or away from the robot. Start at 35 cm, the fastest position in the distance study, about 5.5 cm closer than the CAD position (40.5 cm arms). Once the camera has been shown to detect the screwdrivers reliably from the observation pose, cut the arms to the chosen length.

## Why the distance matters

Board distance changes how far the arm has to swing between picking up a tool and handing it over. In the [pegboard distance study (exp-001)](../../simulation/06_experiments/exp-001-pegboard-distance/), the pickup → handover move at 0.3 speed scaling took:

| Board offset from CAD (m) | −0.07 | −0.05 | 0 (CAD) | +0.05 | +0.10 | +0.15 |
|---|---|---|---|---|---|---|
| Pickup → handover (s) | 2.81 | **3.14** | 3.47 | 3.64 | 3.74 | 3.82 |

Moving 5 cm closer saved 0.34 s (about 10%), the largest gain of any step. Going 2 cm further was still faster, but the arm was close to hitting singularity as seen in [Pickup at −0.07 m](../06_experiments/pegboard-distance/pickup_-0.07.png).

## Options considered

| Option | For | Against |
|---|---|---|
| Fixed at the CAD position (40.5 cm) | Matches the existing CAD and sim; most reach margin | 10% slower handover; no way to tune after testing |
| Fixed at 35 cm | Fastest position found | About 2 cm from the reach limit, and that limit comes from a study with known gaps (see below) |
| **Adjustable, starting at 35 cm** (chosen) | Starts at the fastest position, and can back off if reach or camera view is a problem | Sliding joints can shift, so the position has to be checked after any move |

## Why adjustable

Two things can't be settled in the sim:

1. **Real reach margin.** exp-001 didn't move the board in the collision model; only the pickup target changed. Build tolerances on the frame and brackets add more uncertainty.
2. **Camera view.** The eye-in-hand camera has a fixed focus: soft closer than about 0.2 m, sharp from 0.25 m. If the board is too close, the observation pose may not be able to back off far enough to keep the tools in focus and in frame.

Either one could force the board back out. Making the arms adjustable costs nothing extra, because the 30 mm extrusion already allows sliding and the extrusions haven't been cut yet.

## How to adjust it

1. Loosen the bracket bolts on both arms and slide the board to the new position. Keep both arms the same length so the board stays square.
2. Re-tighten, then repeat the datum check (see [Fixed position](fixed-position.md)).
3. Update the `pegboard_face` frame in `handover_cell` to the new position, so the robot's targets match the board.

## How it will be verified

- **Sim:** re-run the reach check with the board actually moved to −0.05 m in the model.
- **Real robot:** time pickup → handover at 35 cm, then at the CAD position, to confirm the sim's trend.
- **Camera:** confirm all three screwdrivers are detected from the observation pose at 35 cm.

Once all three pass, cut the arms to that length.

## Looking back

The 35 cm figure comes from a study that changed only the pickup target, not the board's position in the collision model. That makes it a useful trend but a weak basis for a final dimension. If we were starting again, we'd make the board offset a model parameter first and run the sweep with the board actually moving. Keeping the arms adjustable is partly a response to that gap. It avoids cutting a final length on evidence we don't fully trust yet.
