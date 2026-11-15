"""
Bezier handover planner (batch): plans the whole path up front.
"""
import numpy as np
from handover_motion.helper import time_law, bezier, find_pull_points, find_orientation


def plan_bezier(p_0, q_start, q_end, palm_base, normal_base,
                duration=2.0, num_samples=50, a_s=0.2, a_a=0.2, lock=0.7):
    """
    Returns:
        times        (N,)   seconds from start
        positions    (N, 3) tool xyz in base_link
        orientations (N, 4) tool quaternion [x, y, z, w] in base_link
    """
    # end point just off the palm
    p_3 = palm_base + 0.01 * normal_base

    # Need help with these dont know how to grab hand vector or robot
    d_a = -normal_base
    d_s = p_3 - p_0

    #find Bezier points
    #TUNING VALUES (a_s, a_a) CHANGED LATER BASED ON TEST
    points = find_pull_points(p_0, p_3, d_s, d_a, a_s, a_a)

    times = np.linspace(0.0, duration, num_samples)
    positions = np.zeros((num_samples, 3))
    orientations = np.zeros((num_samples, 4))
    for i, t in enumerate(times):
        s = time_law(t, duration)
        positions[i] = bezier(points, s)
        orientations[i] = find_orientation(q_start, q_end, s, lock)

    return times, positions, orientations
