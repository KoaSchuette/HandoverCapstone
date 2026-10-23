import scipy
import numpy as np
import math
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from moveit_msgs.srv import GetPositionIK
from tf2_ros import Buffer, TransformListener
from helper import time_law, bezier, find_pull_points, find_orientation
from hand_msgs.msg import Hand

class Planner_node(Node):
    def __init__(self):
        super().__init__("planner_node")
        # client is set up to send end point for IK solution
        self.cli = self.create_client(GetPositionIK,'compute_ik')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = GetPositionIK.Request()
        # lisitener to grab current held too pose
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # lisitener to trigger node
        self.srv = self.create_service(Trigger, 'start_handover', self.handover_callback)
        self.right_hand = None
        #hand tracking subscriber
        self.hand_sub = self.create_subscription(Hand, '/hand/right', self.hand_msg_callback, 10)
    def send_request(self, position, orientation):
        """
        Send bezier position and SLERP rotation at time (s) to get back joint solution at time (s)
        """
        self.req.ik_request.pose_stamped.pose.position.x = float(position[0])
        self.req.ik_request.pose_stamped.pose.position.y = float(position[1])
        self.req.ik_request.pose_stamped.pose.position.z = float(position[2])
        self.req.ik_request.pose_stamped.pose.orientation.x = float(orientation[0])
        self.req.ik_request.pose_stamped.pose.orientation.y = float(orientation[1])
        self.req.ik_request.pose_stamped.pose.orientation.z = float(orientation[2])
        self.req.ik_request.pose_stamped.pose.orientation.w = float(orientation[3])
        return self.cli.call_async(self.req)
    def hand_msg_callback(self, msg):
        self.right_hand = msg
    def handover_callback(self, request , response): #trigger sequence when this fires start 
        
        # first when trigger is set off grab curent position of held tool for starting p0 of bezier curve
        t = self.tf_buffer.lookup_transform('base_link', 'held_tool', rclpy.time.Time())
        
        #pull data from hand and tool orientation for q_start and q_end
        q_start = np.array[(t.transform.rotation.x,t.transform.rotation.y,t.transform.rotation.z,t.transform.rotation.w)]
        q_end = np.array[(self.right_hand.palm_pose.orientation.x,self.right_hand.palm_pose.orientation.y,self.right_hand.palm_pose.orientation.z,self.right_hand.palm_pose.orientation.w)]
        
        #pull data from hand and tool position for p0 and p1
        p_0 = np.array([t.transform.translation.x, t.transform.translation.y, t.transform.translation.z])   # start
        p_3 = np.array([self.right_hand.palm_pose.position.x, self.right_hand.palm_pose.position.y, self.right_hand.palm_pose.position.z])
        
        # Need help with these dont know how to grab hand vector or robot
        d_a = np.array([self.right_hand.palm_direction.x, self.right_hand.palm_direction.y, self.right_hand.palm_direction.z])   
        d_s = np.array([0.0, 1.0, 0.0])
        
        #TUNING VALUES CHANGED LATER BASED ON TEST
        a_s = 0.2
        a_a = 0.2

        #find Bezier points
        points = find_pull_points(p_0, p_3, d_s, d_a, a_s, a_a)

        #CHANGE VALUE FOR HANDOFF DURATION
        duration = 2.0
        #define sample rate
        num_samples = 50
        times = np.linspace(0.0, duration, num_samples)
        for time in times:
            s = time_law(t,duration)
            position = bezier(points, s)
            orientation = find_orientation(q_start,q_end,s,1.5)
            self.send_request(position, orientation)
            
def main():
    pass


if __name__ == '__main__':
    main()
