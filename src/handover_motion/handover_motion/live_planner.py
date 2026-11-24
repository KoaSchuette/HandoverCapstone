import numpy as np
from scipy.spatial.transform import Rotation
from ruckig import Ruckig, InputParameter, OutputParameter, Result

APPROACH_SPEED = 0.05 #Tunning parameter: How fast tool move towards hand

""" six inputs assumed
    x  y  z rx ry rz
    0  1  2 3  4  5
"""

class LivePlanner:
    def __init__(self, dt, ap = 0.1):
        """
        dt --> tick rate start with 0.01
        ap --> apporach distance
        """
        self.otg = Ruckig(6,dt)#goal is to get tick rate to 0.01 then 0.002
        self.inp =InputParameter(6)
        self.out = OutputParameter(6)
        #temp setting need to be played with
        self.inp.max_velocity = [0.25, 0.25, 0.25, 0.5, 0.5, 0.5]
        self.inp.max_acceleration = [0.5, 0.5, 0.5, 1.0, 1.0, 1.0]
        self.inp.max_jerk = [2.0, 2.0, 2.0, 4.0, 4.0, 4.0]

        self.state = 'IDLE'
        self.q_ref = None
        self.r_target = None
        self.approach_distance = ap
        self.task_offset = Rotation.from_euler('y', -90, degrees=True)


    def start(self,p_0,q_start, v_0=None, a_0=None):
        '''
        p_0 --> tool starting position x y z
        q_start --> tool orientation a start position
        '''
        if v_0 is None: v_0 = np.zeros(6)
        if a_0 is None: a_0 = np.zeros(6)
        self.inp.current_velocity = v_0
        self.inp.current_acceleration = a_0



        self.q_ref = Rotation.from_quat(q_start)
        self.inp.current_position = np.concatenate([p_0, np.zeros(3)])
        self.state = 'APPROACH'

    def quat_to_rotvec(self,q):
        '''
        Takes the target quaterion and output a rotation vector(rx ry rz)
        Rotation vector is need for ruckig
        '''
        r = Rotation.from_quat(q)
        r_vec = self.q_ref.inv()*r
        return r_vec.as_rotvec()
        
    def rotvec_to_quat(self,r_vec):
        """
        Takes Roation vector outupted from ruckig
        Turns it back into a quaterion for robot controller
        """
        q = Rotation.from_rotvec(r_vec)
        q_out = self.q_ref * q
        return q_out.as_quat() 

    
    def step(self,p_palm, q_palm, n_palm):
        '''
        p_palm --> Palm position and
        q_palm --> Rotation of the hand in Quaturion format
        n_palm --> vector that point out the back of your hand
        move to the via point first one achieve hit trigger
        '''
        # ── Target variables ────────────────────────────────────────
        v_approach = APPROACH_SPEED
        palm_rot = Rotation.from_quat(q_palm)
        q_goal = (palm_rot*self.task_offset).as_quat()
        self.r_target = self.quat_to_rotvec(q_goal) 
        d_a = -n_palm # swaps vector direction to point in palm direction
        
        # ── Where to aim, based on state ────────────────────────────
        if  self.state == 'APPROACH':  # Move to Via point instead of actual palm position 
            p_via = p_palm - self.approach_distance*d_a
            self.inp.target_position = np.concatenate([p_via,self.r_target])
            self.inp.target_velocity = np.concatenate([(v_approach *d_a), np.zeros(3)])
            self.inp.target_acceleration = np.zeros(6)
        else:  # If not approaching the via point move to Hand position instead
            self.inp.target_position = np.concatenate([p_palm,self.r_target])
            self.inp.target_velocity = np.zeros(6)
            self.inp.target_acceleration = np.zeros(6)

        
        # ── Run Ruckig ──────────────────────────────────────────────
        result = self.otg.update(self.inp,self.out)
        tool_pos = self.out.new_position[0:3]

        # ── Change State ────────────────────────────────────────────
        if self.state == 'APPROACH' and np.linalg.norm(tool_pos-p_via)< 0.02:
            self.state = 'INSERT'
        elif self.state == 'INSERT':
            if result == Result.Finished:
                self.state = 'WAIT_FOR_GRAB'
        elif self.state == 'WAIT_FOR_GRAB':
            if np.linalg.norm(tool_pos-p_palm)>0.02:
                self.state = 'APPROACH'

        # ── Update Ruckig for next step & Ouput data  ───────────────
        self.out.pass_to_input(self.inp)
        new_position = self.out.new_position[0:3]
        new_quaternion = self.rotvec_to_quat(self.out.new_position[3:6])
        return new_position,new_quaternion



