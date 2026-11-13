# Power architecture

## Decision

Power the electromagnet from the control box's internal 24 V supply, step it down to 12 V with an XL4016 buck converter module, and switch it with an IRF540N low-side MOSFET driven by a controller digital output. The circuit is described on the [driver circuit design page](../04_design/driver-circuit.md).

## Context

The electromagnet is rated 12 V DC at 0.84 A (see [electromagnet](electromagnet.md)). The UR5e has two places to power and switch it: the tool I/O connector at the wrist, and the controller I/O inside the control box. Two things shaped the choice:

- **Release timing.** The handover is meant to release the tool as soon as it is triggered, so the magnet has to switch off without delay.
- **Emergency stop.** What the magnet does when the robot is emergency stopped matters while it is holding a tool.

## Options considered

| Option | For | Against |
|---|---|---|
| Tool I/O, 12 V supply | The 12 V supply is rated 11.5 to 12.5 V at 1000 mA typical (2000 mA peak for up to 1 s, 10% duty), above the magnet's 0.84 A. No converter needed. | Needs a Lumberg M8 8-pin cable, which would have to be bought. The power drops to 0 V and the digital outputs go high impedance on an emergency stop. The tool digital outputs are not current-limited. 0.84 A is 84% of the typical rating. |
| **Controller I/O, 24 V supply with buck converter and MOSFET** (chosen) | The magnet keeps its state through an emergency stop. No M8 cable needed. The internal supply is rated for 2 A and the magnet needs about 0.42 A of it. Wiring to the control box is needed anyway for the USB camera. | Needs a buck converter and a separate switching circuit. |

The tool I/O figures are from section 5.7 of the [UR5e user manual (v5.8)](../08_references/UR5e_User_Manual_v5.8.pdf), and the controller I/O figures from section 5.4.

## Why

### Emergency stop behaviour

This decided the choice. The manual states that tool power and outputs shut off on an emergency stop, so a magnet on the tool I/O would drop its tool at the moment the robot stops. The manual does not describe the controller outputs in an emergency stop, so their behaviour rests on a test, in which the magnet kept its state.

The manual states that the tool digital outputs are not current-limited and makes no such statement for the controller I/O. The controller also monitors the current on its 24 V I/O supply, which is the supply the buck converter draws from. Universal Robots error code [C740A21](https://www.universal-robots.com/manuals/EN/HTML/SW5_26/Content/prod-err-codes/topics/CODE_740.html) is raised when that supply draws too much current, so an overcurrent is detected and reported.

### 12 V and the XL4016

The magnet is rated for 12 V and the controller supply is 24 V, so a step-down was needed. The XL4016 module was available.

### Low-side MOSFET

The buck converter module is not designed to be switched by a digital output, so the magnet needs its own switching stage. An IRF540N on the low side of the magnet does this. The digital output drives its gate through a 10 kΩ and 10 kΩ divider, which puts about 12 V on the gate and loads the output with about 1.2 mA. A flyback diode across the magnet handles the inductive load; the simulation with and without it is on the [driver circuit design page](../04_design/driver-circuit.md).

A relay could have done the same job. The MOSFET was chosen for three reasons:
- **Cost.** It is slightly cheaper. A generic IRF540N is $0.28 each against $0.31 for a Songle SRD-12VDC-SL-C 10 A relay at [LCSC](https://www.lcsc.com/product-detail/C30431.html), and a branded IRF540N is [€1.64](https://www.digikey.ie/en/products/detail/infineon-technologies/IRF540NPBF/811869) against [€2.13](https://www.digikey.it/en/products/detail/omron-electronics-inc-emc-div/G5LE-1-E-DC12/1277876) for an Omron G5LE-1-E DC12 relay at DigiKey. The gap is too small to decide the choice on its own.
- **Reliability.** It has no moving contacts to wear.
- **Speed.** It switches as soon as the digital output changes, which the handover release needs.

## Reflection

The chosen route is the more complex of the two. The tool I/O supply would have needed neither the buck converter nor a separate switching stage.
