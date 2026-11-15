import numpy as np
from scipy.spatial.transform import Rotation
from ruckig import Ruckig, InputParameter, OutputParameter, Result

""" six inputs assumed
    x  y  z rx ry rz
    0  1  2 3  4  5
"""

class LivePlanner:
    def __init__(self):
        self.otg = Ruckig(6,0.02)#goal is to get tick rate to 0.01 then 0.002
        self.InputParameter(6)
        self.OutputParameter(6)
        #temp setting need to be played with
        self.max_velocity = [0.25, 0.25, 0.25, 0.5, 0.5, 0.5]
        self.max_acceleration = [0.5, 0.5, 0.5, 1.0, 1.0, 1.0]
        self.max_jerk = [2.0, 2.0, 2.0, 4.0, 4.0, 4.0]
    
