# Handover planner: commit-once vs real-time

> **Status: open.** The commit-once Bézier planner has been built and tested on the real UR5e, and it works. It can't adapt if the operator moves their hand after the plan starts, so we're looking at real-time planners that track the hand live. Ruckig is the next one to test. Its design is not worked out yet.

## Where we are

The first handover planner followed Biagi et al. [1]. When the operator's hand was steady, it read the palm pose once and built a cubic Bézier path that arrives along the palm normal. A quintic time law timed the path, and SLERP handled the tool orientation. Then it converted the path to joint angles with MoveIt IK and sent the whole trajectory to the robot. Once the trajectory was sent, the target was fixed.

That approach looks good on the robot, but it fails if the hand moves after the plan is sent (see [Reflection](#reflection)). So we're exploring planners that keep updating the target while the robot moves.

## Options so far

| Option | Status | For | Against |
|---|---|---|---|
| **Commit-once Bézier path** | Built and tested | Approach direction along the palm set by the path shape; smooth start and stop from the quintic time law; same path every time for the same inputs; backed by the user study in [1] | Target is fixed once the motion starts, so the tool goes to where the hand *was*; IK for 50 samples happens before the robot moves (up to 2.5 s worst case, see [calculations](../03_calculations/path-and-time-law.md#3-ik-time-budget)) |
| **Real-time planner with Ruckig** | Next to test | Retargets from the robot's current state whenever the hand moves; jerk-limited, so motion should stay smooth while it updates [2]; open source | Plans to a target state, not along a shaped path, so the palm-side approach (H4) would have to be built some other way; an unstable hand estimate can make the robot's motion hard to predict [1] |

Other real-time options may be added here as we look into them.

## Testing the commit-once planner

The commit-once Bézier planner was run on the real UR5e and it worked. With the operator's hand held still, the robot waited for the steady-hand check, planned the path and delivered the tool to the hand.

**Video:** [Bézier handover on the real UR5e](../07_data/Handover%20test%20Bezier.mp4)

[TBD: date of the test, number of runs, and anything notable in the video]

## Open questions for testing Ruckig

- **Approach direction (H4).** How to keep the tool coming in from the palm side, for example by retargeting to a point backed off along the palm normal first and then to the palm.
- **Retarget rate.** How often the hand target is updated, and how far the hand has to move before the robot retargets, so the robot does not twitch on small hand jitter.
- **Joint space or Cartesian.** Whether Ruckig runs on the six joints (with IK on each new hand target) or on the tool pose.
- **The 2 s target (H1).** With a time-optimal planner the duration comes from the limits, not a fixed `duration`, so H1 would be checked by measurement (T1).

## Reflection

The commit-once planner works when the operator's hand stays where it was when the plan was made. Its weak point is a moving hand: if the operator moves their hand after the plan has been sent, the robot has no way to adapt. It keeps going to where the hand was, and the handover fails.

This is more likely than it sounds for our setup. We are designing for a no-look grab, where the operator keeps their eyes on their work and holds a hand out for the tool. Since they are not watching the robot, their hand can easily drift during the approach. In our commit-once test the operator was watching and kept their hand still on purpose, so this failure never came up.

Adding real-time path planning closes this gap. If the robot keeps tracking the hand and updates its target during the approach, a moving hand stops being a failure case and becomes something the planner handles. That is why we are moving to real-time planning, and why it matters for the handoff success target (H2).

## Sources

1. F. Biagi, D. Onfiani, S. Silenzi, C. Iani, L. Biagiotti, "Adaptive vs. Static Robot-to-Human Handover: A Study on Orientation and Approach Direction," arXiv:2604.22378, 2026.
2. L. Berscheid, T. Kröger, "Jerk-limited Real-time Trajectory Generation with Arbitrary Target States," *Robotics: Science and Systems XVII*, 2021. arXiv:2105.04830. Code: https://github.com/pantor/ruckig
