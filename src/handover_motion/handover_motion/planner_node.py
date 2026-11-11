from scipy.spatial.transform import Rotation
import numpy as np
import time
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from moveit_msgs.srv import GetPositionIK
from tf2_ros import Buffer, TransformListener
from handover_motion.helper import time_law, bezier, find_pull_points, find_orientation
from handover_interfaces.msg import Hand
from collections import deque
from sensor_msgs.msg import JointState
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class Planner_node(Node):
    def __init__(self):
        super().__init__("planner_node")
        self.srv_group = MutuallyExclusiveCallbackGroup()
        self.ik_group = MutuallyExclusiveCallbackGroup()

        # IK client
        self.cli = self.create_client(GetPositionIK, 'compute_ik', callback_group=self.ik_group)
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = GetPositionIK.Request()

        # TF lisitener to grab pose
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self, spin_thread=True)

        # trigger service
        self.srv = self.create_service(Trigger, 'start_handover', self.handover_callback,callback_group=self.srv_group)

        # hand tracking
        self.right_hand = None
        self.hand_sub = self.create_subscription(Hand, '/hand/right', self.hand_msg_callback, 10)

        self.declare_parameter('controller_name', 'scaled_joint_trajectory_controller')
        controller_name = self.get_parameter('controller_name').value
        self.traj_client = ActionClient(self, FollowJointTrajectory,
                                        f'/{controller_name}/follow_joint_trajectory')
        self.joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                            'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
    def send_request(self, position, orientation):
        """
        Send bezier position and SLERP rotation at time (s) to get back joint solution at time (s)
        """
        self.req.ik_request.group_name = 'manipulator'
        self.req.ik_request.pose_stamped.header.frame_id = 'base_link'
        self.req.ik_request.avoid_collisions = True
        self.req.ik_request.timeout.sec = 0
        self.req.ik_request.timeout.nanosec = 50_000_000   # 0.05 s 
        self.req.ik_request.pose_stamped.pose.position.x = float(position[0])
        self.req.ik_request.pose_stamped.pose.position.y = float(position[1])
        self.req.ik_request.pose_stamped.pose.position.z = float(position[2])
        self.req.ik_request.pose_stamped.pose.orientation.x = float(orientation[0])
        self.req.ik_request.pose_stamped.pose.orientation.y = float(orientation[1])
        self.req.ik_request.pose_stamped.pose.orientation.z = float(orientation[2])
        self.req.ik_request.pose_stamped.pose.orientation.w = float(orientation[3])
        result = self.cli.call(self.req)
        if result.error_code.val != 1:
            self.get_logger().warn(
                f'IK failed: code {result.error_code.val}, pos {np.round(position, 3)}')
            return None
        self.req.ik_request.robot_state.joint_state = result.solution.joint_state

        return result.solution.joint_state

    def hand_msg_callback(self, msg):
        self.right_hand = msg
    def handover_callback(self, request , response): #trigger sequence when this fires start 
        hand_steady = False
        while not hand_steady:
            # dont need fallback OTP point yet later TODO
            hand = self.wait_for_steady_hand()
            if hand is not None:
                hand_steady = True
                # for now waiting till it sees a hand
        
            time.sleep(0.05)
        
    

        # first when trigger is set off grab curent position of held tool for starting p0 of bezier curve
        tool_tf = self.tf_buffer.lookup_transform('base_link', 'held_tool', rclpy.time.Time())
        leap_tf = self.tf_buffer.lookup_transform('base_link', 'leap_link', rclpy.time.Time())
        #rotation matric given from sim
        r = leap_tf.transform.rotation
        R_leap = Rotation.from_quat([r.x, r.y, r.z, r.w])
        #sensor data
        o = hand.palm_pose.orientation
        R_palm = Rotation.from_quat([o.x, o.y, o.z, o.w])

        
        #pull data from hand and tool orientation for q_start and q_end
        q_start = np.array([tool_tf.transform.rotation.x,tool_tf.transform.rotation.y,tool_tf.transform.rotation.z,tool_tf.transform.rotation.w])
        # q_end = (R_leap * R_palm).as_quat()
        q_end = q_start
        #translation from leap to base
        t_leap = leap_tf.transform.translation
        offset = np.array([t_leap.x, t_leap.y, t_leap.z])

        # raw leap data
        pp = hand.palm_pose.position
        palm_leap = np.array([pp.x, pp.y, pp.z])
        n = hand.palm_normal
        normal_leap = np.array([n.x, n.y, n.z])

        # translate into base_link
        palm_base = R_leap.apply(palm_leap) + offset
        normal_base = R_leap.apply(normal_leap)

        #pull data from hand and tool position for p0 and p1
        p_0 = np.array([tool_tf.transform.translation.x, tool_tf.transform.translation.y, tool_tf.transform.translation.z])
        p_3 = palm_base + 0.01 * normal_base 
        
        # Need help with these dont know how to grab hand vector or robot
        d_a = -normal_base
        d_s = p_3 - p_0
        self.get_logger().info(f'p_0 {np.round(p_0, 3)}  p_3 {np.round(p_3, 3)}  d_a {np.round(d_a, 3)}')
        #TUNING VALUES CHANGED LATER BASED ON TEST
        a_s = 0.2
        a_a = 2

        #find Bezier points
        points = find_pull_points(p_0, p_3, d_s, d_a, a_s, a_a)

        #CHANGE VALUE FOR HANDOFF DURATION
        duration = 2.0
       
        #define sample rate
        num_samples = 50
       
        times = np.linspace(0.0, duration, num_samples)
        
        # TO IK solver
        self.req.ik_request.robot_state.joint_state = JointState()
        solutions = np.zeros((num_samples, 6)) 
        for i,t in enumerate(times):
            s = time_law(t,duration)
            position = bezier(points, s)
            orientation = find_orientation(q_start,q_end,s,0.7)

            joint_state = self.send_request(position, orientation)
            if joint_state is None:
                response.success = False
                response.message = f'IK failed at t = {t:.2f} s'
                return response
            angles = dict(zip(joint_state.name, joint_state.position))
            solutions[i] = [angles[name] for name in self.joint_names]

        # find velocity
        max_speed = 6# rad/s, joint speed
        max_accel = 10# rad/s^2, placeholder
        sample_dt = duration / (num_samples - 1)# time between neighbouring samples

        velocity = np.zeros((num_samples, 6))
        dq = solutions[2:] - solutions[:-2]
        dt = times[2:] - times[:-2]
        velocity[1:-1] = dq / dt[:, None]

        # check for jumps and max speed
        for i in range(len(velocity) - 1):
            joint_speed = np.abs(velocity[i]).max()
            joint_accel = np.abs((velocity[i + 1] - velocity[i]) / sample_dt).max()

            if joint_accel > max_accel:
                self.get_logger().warn(f'Joint acceleration too high: {joint_accel:.2f} rad/s^2 at sample {i}')
                response.success = False
                response.message = f'Joint acceleration too high: {joint_accel:.2f} rad/s^2 at sample {i}'
                return response
            if joint_speed > max_speed:
                self.get_logger().warn(f'Joint speed too high: {joint_speed:.2f} rad/s at sample {i}')
                response.success = False
                response.message = f'Joint speed too high: {joint_speed:.2f} rad/s at sample {i}'
                return response

        self.get_logger().info(f'IK ok for all {len(solutions)} samples')
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        for i, t in enumerate(times):
            point = JointTrajectoryPoint()
            point.positions = solutions[i].tolist()
            point.velocities = velocity[i].tolist()
            point.time_from_start = Duration(sec=int(t), nanosec=int((t - int(t)) * 1e9))
            traj.points.append(point)
        
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj
        self.traj_client.send_goal_async(goal)
        response.success = True
        response.message = 'trajectory sent'
        return response
    
    def wait_for_steady_hand(self, timeout=10.0):
        window = deque(maxlen=10)
        speed_threshold = 0.05 
        max_age = 0.2
        last_stamp = None


        start = time.monotonic()    
        while time.monotonic() - start < timeout:
            hand = self.right_hand
            if hand is not None:
                
                age = (self.get_clock().now() - rclpy.time.Time.from_msg(hand.header.stamp)).nanoseconds / 1e9
                #check for new hand msg
                is_new = hand.header.stamp != last_stamp
                if age > max_age:
                    window.clear()
                elif is_new:
                    v = hand.palm_velocity
                    window.append(np.linalg.norm([v.x, v.y, v.z]))
                    last_stamp = hand.header.stamp
                    if len(window) == window.maxlen and sum(window) / len(window) < speed_threshold:
                        return hand
            time.sleep(0.05)
        return None
def main():   
    rclpy.init()
    node = Planner_node()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
