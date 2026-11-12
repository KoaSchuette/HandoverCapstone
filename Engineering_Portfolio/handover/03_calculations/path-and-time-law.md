# Path geometry, time law and timing bounds

Worked checks on the **commit-once Bézier planner** in `handover_motion/helper.py` and `planner_node.py`. This planner was built and tested on the real UR5e.

Parameter values are the ones in `planner_node.py`. The plotting script [`test_path.py`](../../../src/handover_motion/handover_motion/test_path.py) draws the path shape and the time-law spacing for a 2D test case.

## Notation

| Symbol | Meaning | Code |
|---|---|---|
| $\mathbf{p}_0$ | Tool position at the start (base frame) | `p_0`, from TF `base_link → held_tool` |
| $\mathbf{p}_3$ | Target: palm position pushed 0.01 m out along the palm normal | `p_3 = palm_base + 0.01 * normal_base` |
| $\hat{\mathbf{n}}$ | Unit palm normal in the base frame | `normal_base` |
| $\hat{\mathbf{d}}_s$ | Start direction (unit) | `p_3 - p_0`, normalized |
| $\hat{\mathbf{d}}_a$ | Approach direction (unit) | `-normal_base` |
| $\alpha_s,\ \alpha_a$ | Start and approach scale factors (m) | `a_s = 0.2`, `a_a = 0.2` |
| $T$ | Motion duration | `duration = 2.0` s |
| $\tau$ | Normalized time, $\tau = t/T$ | |

The two middle control points (Biagi et al. [1], section III-D) are

$$
\mathbf{p}_1 = \mathbf{p}_0 + \alpha_s\,\hat{\mathbf{d}}_s
\qquad\qquad
\mathbf{p}_2 = \mathbf{p}_3 - \alpha_a\,\hat{\mathbf{d}}_a = \mathbf{p}_3 + \alpha_a\,\hat{\mathbf{n}}
$$

## 1. How far the control points bend the path

The cubic Bézier path is

$$
\mathbf{B}(s) = (1-s)^3\,\mathbf{p}_0 + 3s(1-s)^2\,\mathbf{p}_1 + 3s^2(1-s)\,\mathbf{p}_2 + s^3\,\mathbf{p}_3,
\qquad s \in [0,1]
$$

**End tangents.** Differentiating and evaluating at the ends:

$$
\mathbf{B}'(0) = 3(\mathbf{p}_1 - \mathbf{p}_0) = 3\alpha_s\,\hat{\mathbf{d}}_s
\qquad\qquad
\mathbf{B}'(1) = 3(\mathbf{p}_3 - \mathbf{p}_2) = 3\alpha_a\,\hat{\mathbf{d}}_a
$$

The path arrives along $\hat{\mathbf{d}}_a = -\hat{\mathbf{n}}$, so the tool moves *into* the palm along its normal. This is what requirement H4 asks for.

**Midpoint.** Substituting $\mathbf{p}_1$ and $\mathbf{p}_2$ at $s = 0.5$:

$$
\mathbf{B}(0.5) = \frac{\mathbf{p}_0 + 3\mathbf{p}_1 + 3\mathbf{p}_2 + \mathbf{p}_3}{8}
= \underbrace{\frac{\mathbf{p}_0 + \mathbf{p}_3}{2}}_{\text{chord midpoint}}
+ \frac{3}{8}\left(\alpha_s\,\hat{\mathbf{d}}_s - \alpha_a\,\hat{\mathbf{d}}_a\right)
$$

Since $\hat{\mathbf{d}}_s$ points along the straight line, the $\alpha_s$ term only slides the midpoint along the chord. The $\alpha_a$ term pushes it sideways, along the palm normal, by

$$
\Delta_{\text{mid}} = \frac{3}{8}\,\alpha_a
$$

| $\alpha_a$ (m) | $\Delta_{\text{mid}}$, midpoint pushed out along the palm normal (m) |
|:---:|:---:|
| 0.1 | 0.04 |
| **0.2 (current)** | **0.075** |
| 0.3 | 0.11 |
| 0.5 | 0.19 |

With $\alpha_a = 0.2$ the path bows 0.075 m (7.5 cm) away from the straight line at its midpoint. That gives a gentle curve that still lines the tool up with the palm normal at the end, without swinging far out of the way. For scale, the UR5e's reach is 850 mm [2], so the bend is small compared with the workspace.

## 2. Time law

The path parameter follows a quintic polynomial in normalized time:

$$
s(\tau) = 10\tau^3 - 15\tau^4 + 6\tau^5, \qquad \tau = \frac{t}{T} \in [0,1]
$$

Its derivatives with respect to real time $t$ are

$$
\dot{s} = \frac{30\,\tau^2(1-\tau)^2}{T}
\qquad\qquad
\ddot{s} = \frac{60\,\tau(1-\tau)(1-2\tau)}{T^2}
\qquad\qquad
\dddot{s} = \frac{60 - 360\,\tau + 360\,\tau^2}{T^3}
$$

| Quantity | Start ($\tau = 0$) | End ($\tau = 1$) | Peak |
|---|:---:|:---:|---|
| Speed $\dot{s}$ | $0$ | $0$ | $1.875/T$ at $\tau = 0.5$ |
| Acceleration $\ddot{s}$ | $0$ | $0$ | $\pm 5.774/T^2$ at $\tau = 0.211$ and $0.789$ |
| Jerk $\dddot{s}$ | $60/T^3$ | $60/T^3$ | $60/T^3$ (bounded, not zero) |

Peaks were found analytically ($\ddot{s}$ peaks where $\dddot{s} = 0$, at $\tau = \tfrac{3 \mp \sqrt{3}}{6}$, giving $10/\sqrt{3} \approx 5.774$) and checked numerically.

Zero speed and acceleration at $\tau = 1$ means the tool comes to a smooth stop at the hand (requirement H3). Jerk is finite but not zero at the ends. The duration $T = 2.0$ s matches the H1 target of 2 s for the handover motion.

**What this means in metres.** If the path length is $L$, the tool's peak speed and acceleration are

$$
v_{\max} = 1.875\,\frac{L}{T}
\qquad\qquad
a_{\max} = 5.774\,\frac{L}{T^2}
$$

For $T = 2.0$ s, that is $v_{\max} = 0.94\,L$ m/s and $a_{\max} = 1.44\,L$ m/s². $L$ is not logged yet; add it to the planner log so these can be checked per handover.

## 3. IK time budget

| Item | Value | From |
|---|---|---|
| Samples $N$ | 50 | `num_samples` |
| Spacing $\Delta t = T/(N-1)$ | 0.041 s | |
| IK timeout per call $t_{\text{IK}}$ | 0.05 s | `ik_request.timeout` |
| Worst-case IK time before motion | 2.5 s | $N \cdot t_{\text{IK}}$ |

$$
t_{\text{IK, worst}} = N \cdot t_{\text{IK}} = 50 \times 0.05\ \text{s} = 2.5\ \text{s} \;>\; T = 2.0\ \text{s}
$$

In the worst case, the IK pass alone takes longer than the motion. The typical time is probably far below the worst case, because each call is seeded with the previous solution, but it has not been measured. **TBD: log IK time per handover.**

## 4. Joint limit check

`planner_node` estimates joint speed with a central difference over the samples and acceleration by differencing those speeds:

$$
\dot{q}_i \approx \frac{q_{i+1} - q_{i-1}}{t_{i+1} - t_{i-1}}
\qquad\qquad
\ddot{q}_i \approx \frac{\dot{q}_{i+1} - \dot{q}_i}{\Delta t}
$$

It then rejects the trajectory if any joint goes above its limits.

| Limit | In `planner_node` | UR5e datasheet [2] | Our MoveIt config |
|---|:---:|:---:|:---:|
| Joint speed | 6 rad/s | $180^\circ/\text{s} = \pi \approx 3.14$ rad/s (all joints) | $\pi$ rad/s |
| Joint acceleration | 10 rad/s² ("placeholder") | not given | 2.0 rad/s² |

The planner's speed check is almost twice the robot's hardware limit, so it cannot catch a trajectory the robot can't follow. Lower both checks to at most the MoveIt config values.

## 5. Orientation lock

`find_orientation(q_start, q_end, s, 0.7)` runs SLERP over $s \in [0,\ 0.7]$ and holds the final orientation after that:

$$
\mathbf{q}(s) =
\begin{cases}
\operatorname{slerp}\!\left(\mathbf{q}_{\text{start}},\ \mathbf{q}_{\text{end}},\ \dfrac{s}{0.7}\right) & s \le 0.7 \\[2ex]
\mathbf{q}_{\text{end}} & s > 0.7
\end{cases}
$$

From the time law, $s = 0.7$ at $\tau \approx 0.61$, so with $T = 2.0$ s the tool reaches its final orientation about 1.2 s into the motion and only translates for the last 0.8 s. This matches the paper's intent that the orientation settles before the tool reaches the hand [1]. (Right now $\mathbf{q}_{\text{end}} = \mathbf{q}_{\text{start}}$, so nothing rotates yet.)

## 6. Leap to base transform

The Ultraleap node publishes in `leap_link` and already converts mm to m. The planner maps the palm into the base frame with the static TF `base_link → leap_link`, with rotation $\mathbf{R}$ and translation $\mathbf{t}$:

$$
\mathbf{p}_{\text{palm}}^{\,\text{base}} = \mathbf{R}\,\mathbf{p}_{\text{palm}}^{\,\text{leap}} + \mathbf{t}
\qquad\qquad
\hat{\mathbf{n}}^{\,\text{base}} = \mathbf{R}\,\hat{\mathbf{n}}^{\,\text{leap}}
$$

The normal is a direction, so only the rotation applies. The accuracy of `leap_link` in the URDF directly limits handover accuracy (R6). **TBD: measure the Ultraleap mount pose on the real cell and compare with the URDF.**

## Sources

1. F. Biagi et al., "Adaptive vs. Static Robot-to-Human Handover: A Study on Orientation and Approach Direction," arXiv:2604.22378, 2026.
2. Universal Robots, UR5e datasheet. https://www.crossco.com/wp-content/uploads/2024/04/UR5e-Datasheet.pdf
