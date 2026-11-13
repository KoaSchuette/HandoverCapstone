# End effector requirements

These requirements break the project requirements (R2, R3, R4, R5 and R7 in the [portfolio start page](../../README.md)) down to the end effector, and add the conditions it has to meet for the system to work as a whole: the robot's electrical and mechanical limits, the safety requirements in section 5.0 of the proposal, and the camera that rides on it. Deciding when to release a tool is outside this subsystem. The end effector releases the tool when the magnet is switched off.

Numbers either trace to a source in the **Source** column or are marked **TBD**. A TBD value is set from the first measurement and recorded here.

## Requirements

| ID | Requirement | Value | Parent | Source | Verified by |
|---|---|---|---|---|---|
| E1 | The magnet holds the tool with no slip through a full handoff motion | Up to 0.45 kg, no visible slip | R3 | Proposal Table 2; [magnet feasibility](../03_calculations/magnet-feasibility.md) (minimum margin 3.2) | T1 |
| E2 | The same magnet holds all three screwdrivers by their steel shafts | 3 tools, 6.35 mm (1/4 in) shaft | R4, R5 | [Magnet feasibility](../03_calculations/magnet-feasibility.md) | T2 |
| E3 | Switching the magnet off releases the tool | Delay from output off to release: TBD | R2, R1 | Proposal section 3.2.2 (release at handover) | T3 |
| E4 | The magnet keeps holding the tool through an emergency stop | Magnet stays energised, tool stays held | Safety (proposal section 5.0) | Proposal section 5.0; UR5e manual section 4.3 [1] | T4 |
| E5 | The magnet circuit draws less current than the controller's internal 24 V supply provides | ≤ 2 A at the PWR terminal (about 0.42 A expected) | System | UR5e manual section 5.4.1 [1]; [power architecture](../02_decisions/power-architecture.md) | T5 |
| E6 | The magnet does not heat its mount past a safe temperature at the highest duty cycle in use | Duty cycle up to 50%; mount well below 55 °C | R3 | Glass transition of PLA, 55 to 60 °C [3]. Staying below it also keeps a brief touch from causing injury | T6 |
| E7 | The magnet fits within the robot's mounting flange | ≤ 63 mm diameter | System | [Electromagnet decision](../02_decisions/electromagnet.md) | T7 |
| E8 | The end effector bolts to the tool flange without damaging it | Four M6 holes (ISO 9409-1-50-4-M6), bolts no longer than 8 mm | System | UR5e manual section 4.3 [1] | T7 |
| E9 | The total mass of the end effector and its payload is within the robot's payload rating | < 5 kg | System | UR5e manual section 4.4 and appendix D [1] | T7 |
| E10 | The camera stays fixed relative to the tool flange between calibration and use | No movement | R5 | Proposal sections 6.1 and 6.2 [2] | T8 |
| E11 | The tool held on the magnet is visible to the camera, so the camera can confirm the pickup | Tool visible in the image when held | R5 | Proposal section 6.2 [2] | T8 |
| E12 | The cable is not worn or damaged by the end effector's motion | Wire relief clamps fitted; bend radius recorded for the poses used | System (reliability over 96 trials) | Team requirement | T9 |
| E13 | The end effector can be rebuilt from this folder: CAD, wiring, circuit and settings | A lab member outside the team can follow it | R7 | Proposal Table 2 [2] | R7 test |

## Test plan

| Test | What | How | Pass |
|---|---|---|---|
| T1 | Holding force at the payload limit | Move a 0.45 kg steel-shafted test object through a full handoff motion on the real robot. Also count drops in the shared trials. | No visible slip and no drops (E1) |
| T2 | Pickup of all three tools | Part of the final evaluation: 48 delivery and 48 return trials with each tool requested 16 times. Record each pickup and any drop. | Every tool is picked up and held in the trials (E2) |
| T3 | Release delay | Record the output switching off and the tool leaving the magnet face on slow-motion video, and measure the delay between them. | Delay recorded and set as the value in E3, checked against the handover time budget in R1 |
| T4 | Emergency stop | With the tool or test object held and a second team member ready at the teach pendant, trigger an emergency stop and a protective stop over a padded surface. | Magnet stays energised and the tool stays held (E4) |
| T5 | Supply current | Measure the current at the PWR terminal with the magnet on. | ≤ 2 A (E5) |
| T6 | Mount temperature | Switch the magnet on and off at a 50% duty cycle for a run as long as an evaluation session and measure the temperature of the mount next to the magnet. | Well below 55 °C (E6) |
| T7 | Fit, flange mounting and mass | Measure the magnet and the mount against the CAD, check the bolt lengths against the flange, and weigh the assembled end effector. | Dimensions and bolts meet E7 and E8, and the mass is below 5 kg (E9) |
| T8 | Camera mount and view | Calibrate the camera, run the shared trials, then check the calibration again. Hold a tool on the magnet and check it is visible in the image. | Calibration unchanged and the tool visible (E10, E11) |
| T9 | Cable wear | Rotate wrist 3 through the poses the subroutines use with the cable and sleeve fitted, record the bend radius where the cable leaves the clamp, and inspect the cable for wear and damage before and after the trials. | No wear or damage, and the bend radius recorded (E12) |

## Sources

1. Universal Robots, [UR5e user manual, version 5.8](../08_references/UR5e_User_Manual_v5.8.pdf). Section 4.3 (tool flange, bolt length, dropped-part hazard), section 4.4 (maximum payload), section 5.4.1 (controller 24 V supply) and appendix D (technical specifications).
2. MREN 403 Group 16, [project proposal](../../deliverables/project-proposal.pdf), October 9, 2026. Table 2 (R1 to R7), section 3.2 (subroutines), section 5.0 (safety) and section 6 (methods).
3. SpecialChem, "Polylactic Acid (PLA): How to select the right grade?", glass transition temperature of 55 to 60 °C. https://www.specialchem.com/plastics/guide/polylactide-pla-bioplastic
