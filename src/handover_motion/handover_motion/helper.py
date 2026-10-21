import math
import numpy as np

def bezier(points,s):
    return  points[0]*(1-s)**3+3*s*points[1]*(1-s)**2 +3*points[2]*(1-s)*s**2+ points[3]*s**3


def time_law(time, duration):
    if duration <= 0:
            raise ValueError("invalid duration: please enter a duration above 0")
    if time < 0:
        return 0
    if time > duration:
        return 1
    tau = time/duration
    s = 10*tau**3 - 15*tau**4 + 6*tau**5
    return s

def find_pull_points(p_0, p_3, d_s ,d_a,a_s,a_a):
     d_s = d_s / np.linalg.norm(d_s)
     d_a = d_a / np.linalg.norm(d_a)
     p_1 = p_0 + a_s*d_s
     p_2 = p_3 - a_a*d_a
     points = np.array([p_0,p_1,p_2,p_3])
     return points