# Frame and brackets

## Decision

Build the pegboard uprights and arms from 30 mm aluminium extrusion instead of matching the cart's 45 mm Vention extrusion. Custom angle brackets join the two sizes.

## Options considered

| Option | Cost | For | Against |
|---|---|---|---|
| Vention 45 × 45 mm parts, matched to the cart | ≈ $351 | Same system as the cart; off-the-shelf gussets; matches the CAD | More expensive |
| **30 mm extrusion + custom brackets** (chosen) | $281.85 + bracket material | About $69 cheaper; still T-slot, so the arms can slide | Two extrusion sizes and hardware sets; brackets must be designed and made |

## Why

The 30 mm extrusion was cheaper. Both options are T-slot extrusion, so the frame stays adjustable either way (see [adjustable arms](adjustable-arms.md)).

## Consequences

- The brackets set the board's position. They are not designed yet; their design will be added to [`04_design/`](../04_design/) once they're printed. If printed brackets flex or creep under load, the board will drift, so the position will be re-checked after the first week of use.
- The CAD and the sim mesh still show 45 mm Vention parts. They need updating once the frame is built.

## Looking back

The switch to 30 mm happened at ordering, after the CAD was finished, so the model no longer matches the build. Settling the frame size before finalizing the CAD, or updating the CAD as soon as it changed, would have kept the two in sync.
