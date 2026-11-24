from scipy.spatial.transform import Rotation
import numpy as np
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from std_srvs.srv import Trigger
from geometry_msgs.msg import PoseStamped
from moveit_msgs.srv import GetPositionIK, ServoCommandType
from tf2_ros import Buffer, TransformListener
from handover_motion.bezier_planner import plan_bezier
from handover_motion.live_planner import LivePlanner
from handover_interfaces.msg import Hand
from collections import deque
from sensor_msgs.msg import JointState
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


MAX_AGE = 0.2

class Planner_node(Node):
    def __init__(self):
        super().__init__("planner_node")
        self.srv_group = MutuallyExclusiveCallbackGroup()
        self.live_group = MutuallyExclusiveCallbackGroup()
        self.ik_group = MutuallyExclusiveCallbackGroup()

        # IK client
        self.cli = self.create_client(GetPositionIK, 'compute_ik', callback_group=self.ik_group)
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = GetPositionIK.Request()
        # Servo mode-switch client (no wait loop, so the node still starts without Servo)
        self.servo_cli = self.create_client(ServoCommandType, '/servo_node/switch_command_type',
                                            callback_group=self.ik_group)

        # TF lisitener to grab pose
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self, spin_thread=True)

        # trigger service
        self.srv = self.create_service(Trigger, 'start_handover', self.handover_callback,callback_group=self.srv_group)
        self.srv_rukig = self.create_service(Trigger, 'start_rukig_handover', self.rukig_handover_callback,callback_group=self.srv_group)

        # stop trigger service
        self.srv_stop = self.create_service(Trigger, 'stop_handover', self.stop_handover_callback, callback_group=self.srv_group)

        # hand tracking
        self.right_hand = None
        self.hand_sub = self.create_subscription(Hand, '/hand/right', self.hand_msg_callback, 10)

        # get joint states from real or sim controller
        # self.joint_states = None
        # self.joint_states_sub = self.create_subscription(JointState,'/joint_states', self.joint_states_callback,10)

        self.declare_parameter('controller_name', 'scaled_joint_trajectory_controller')
        controller_name = self.get_parameter('controller_name').value
        self.traj_client = ActionClient(self, FollowJointTrajectory,f'/{controller_name}/follow_joint_trajectory')
        self.joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint','wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

        # Rukig Variables
        self.ruckig_planner = None #Planner object
        self.dt = 0.02 #frequency to call next step TUNING PARAMETER aim for 0.01 100Hz` `
        self.ruckig_timer = None  #inialize the timer as nothing

        #Rukig Robot Publisher to Controller
        # self.forward_position_pub = self.create_publisher(Float64MultiArray, '/forward_position_controller/commands',10)
        # Rukig Servo Publisher
        self.servo_pub = self.create_publisher(PoseStamped,'/servo_node/pose_target_cmds',10)

    # ------------------------------------------------------------------
    # subscriber callbacks
    # ------------------------------------------------------------------
    def joint_states_callback(self, msg):
        self.joint_states = msg

    def hand_msg_callback(self, msg):
        self.right_hand = msg

    # ------------------------------------------------------------------
    # trigger callbacks (one per planner)
    # ------------------------------------------------------------------
    def handover_callback(self, request , response): #trigger sequence when this fires start
        """Bezier planner (batch): plan whole path, IK every sample, send once."""
        hand_steady = False
        while not hand_steady:
            # dont need fallback OTP point yet later TODO
            hand = self.wait_for_steady_hand()
            if hand is not None:
                hand_steady = True
                # for now waiting till it sees a hand
            time.sleep(0.05)

        p_0, q_start, palm_base, normal_base, q_palm = self.get_hand_in_base(hand)
        q_end = q_palm
        # q_end = q_start

        times, positions, orientations = plan_bezier(p_0, q_start, q_end, palm_base, normal_base)
        self.get_logger().info(
            f'p_0 {np.round(p_0, 3)}  p_3 {np.round(positions[-1], 3)}  d_a {np.round(-normal_base, 3)}')

        solutions, fail_t = self.solve_ik_path(times, positions, orientations)
        if solutions is None:
            response.success = False
            response.message = f'IK failed at t = {fail_t:.2f} s'
            return response

        velocity, error = self.check_joint_limits(times, solutions)
        if error is not None:
            self.get_logger().warn(error)
            response.success = False
            response.message = error
            return response

        self.get_logger().info(f'IK ok for all {len(solutions)} samples')
        self.send_trajectory(times, solutions, velocity)
        response.success = True
        response.message = 'trajectory sent'
        return response

    def rukig_handover_callback(self, request, response):  # TESTING
        """Live planner (streaming).
           initalize the ruckig object and starts the planner
           Creates a timer to step through the s
        """
        # put Servo in pose mode
        if not self.servo_cli.service_is_ready():
            response.success = False
            response.message = 'Servo not running'
            return response
        servo_req = ServoCommandType.Request()
        servo_req.command_type = ServoCommandType.Request.POSE
        servo_result = self.servo_cli.call(servo_req)
        if not servo_result.success:
            response.success = False
            response.message = 'Servo mode switch failed'
            return response

        if self.ruckig_timer is not None:
            response.success = False
            response.message = 'Planner Already running'
            return response
        elif self.right_hand is None:
            #TODO add edge case to move to a predicted point if no hand is detected
            response.success = False
            response.message = 'No Hand detected'
            return response

        #Start the planner
        self.ruckig_planner = LivePlanner(self.dt)
        p_0, q_start, palm_base, normal_base, q_palm = self.get_hand_in_base(self.right_hand)
        self.ruckig_planner.start(p_0,q_start)
        self.ruckig_timer = self.create_timer(self.dt, self.ruckig_step,callback_group=self.live_group)  #Start timere to call the step function ever tick

        response.success = True
        response.message = 'Ruckig Handover started'
        return response
    def ruckig_step(self):
        # msg = Float64MultiArray()
        new_msg = PoseStamped()
        new_msg.header.frame_id = 'base_link'
        new_msg.header.stamp = self.get_clock().now().to_msg()
        hand = self.right_hand
        age = (self.get_clock().now()-rclpy.time.Time.from_msg(hand.header.stamp)).nanoseconds/1e9
        if age > MAX_AGE:
            self.get_logger().info("stale msg detected", throttle_duration_sec=1.0)
            return
        p_0, q_start, palm_base, normal_base, q_palm = self.get_hand_in_base(hand)
        position, quaterion = self.ruckig_planner.step(palm_base, q_palm, normal_base)
        # joint_state = self.send_request(position,quaterion)
        # if joint_state is None:
        #     return
        # msg.data = list(joint_state.position)
        new_msg.pose.position.x = float(position[0])
        new_msg.pose.position.y = float(position[1])
        new_msg.pose.position.z = float(position[2])
        new_msg.pose.orientation.x = float(quaterion[0])
        new_msg.pose.orientation.y = float(quaterion[1])
        new_msg.pose.orientation.z = float(quaterion[2])
        new_msg.pose.orientation.w = float(quaterion[3])
        self.servo_pub.publish(new_msg)
        # self.forward_position_pub.publish(msg)



    def stop_handover_callback(self, request, response):
        if self.ruckig_timer is not None:
            self.ruckig_timer.cancel()
            self.destroy_timer(self.ruckig_timer)
            self.ruckig_timer = None
            response.success = True
            response.message = 'Timer stopped'
        else:
            response.success = False
            response.message = 'No Timer to Stop'
        return response
    

    # ------------------------------------------------------------------
    # shared helpers (any planner can use these)
    # ------------------------------------------------------------------
    def get_hand_in_base(self, hand):
        """
        puts hand position in base link frame
        """
        # first when trigger is set off grab curent position of held tool
        tool_tf = self.tf_buffer.lookup_transform('base_link', 'held_tool', rclpy.time.Time())
        leap_tf = self.tf_buffer.lookup_transform('base_link', 'leap_link', rclpy.time.Time())
        #rotation matric given from sim
        r = leap_tf.transform.rotation
        R_leap = Rotation.from_quat([r.x, r.y, r.z, r.w])
        #sensor data
        o = hand.palm_pose.orientation
        R_palm = Rotation.from_quat([o.x, o.y, o.z, o.w])

        #pull data from tool orientation and position
        t = tool_tf.transform
        q_start = np.array([t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w])
        p_0 = np.array([t.translation.x, t.translation.y, t.translation.z])

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
        q_palm = (R_leap * R_palm).as_quat()

        return p_0, q_start, palm_base, normal_base, q_palm

    def send_request(self, position, orientation):
        """
        sends position to ik solver form moveit returns in joint state
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

    def solve_ik_path(self, times, positions, orientations):
        """
        uses send_request over en entire path returns the solution to be sent the controller
        """
        # clear seed so first IK seeds from MoveIt's current state
        self.req.ik_request.robot_state.joint_state = JointState()
        solutions = np.zeros((len(times), 6))
        for i, t in enumerate(times):
            joint_state = self.send_request(positions[i], orientations[i])
            if joint_state is None:
                return None, t
            angles = dict(zip(joint_state.name, joint_state.position))
            solutions[i] = [angles[name] for name in self.joint_names]
        return solutions, None

    def check_joint_limits(self, times, solutions, max_speed=10.0, max_accel=30.0):
        """
        Checks if joint limits are reach and path is valid 
        also prevent large jerks
        Finite-difference joint velocity and check speed / accel limits.
        max_speed rad/s, max_accel rad/s^2 (placeholder)
        Returns (velocity (N,6), None) or (velocity, error message)
        """
        num_samples = len(times)
        sample_dt = (times[-1] - times[0]) / (num_samples - 1)# time between neighbouring samples

        velocity = np.zeros((num_samples, 6))
        dq = solutions[2:] - solutions[:-2]
        dt = times[2:] - times[:-2]
        velocity[1:-1] = dq / dt[:, None]

        # check for jumps and max speed
        for i in range(len(velocity) - 1):
            joint_speed = np.abs(velocity[i]).max()
            joint_accel = np.abs((velocity[i + 1] - velocity[i]) / sample_dt).max()
            if joint_accel > max_accel:
                return velocity, f'Joint acceleration too high: {joint_accel:.2f} rad/s^2 at sample {i}'
            if joint_speed > max_speed:
                return velocity, f'Joint speed too high: {joint_speed:.2f} rad/s at sample {i}'
        return velocity, None

    def send_trajectory(self, times, solutions, velocity):
        """Pack joint solutions into a JointTrajectory and send to the controller."""
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

    def wait_for_steady_hand(self, timeout=10.0):
        window = deque(maxlen=10)
        speed_threshold = 0.10 # change me
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
                    speed = np.linalg.norm([v.x, v.y, v.z])
                    window.append(speed)
                    last_stamp = hand.header.stamp
                    # self.get_logger().info(
                        # f'speed {speed:.3f} m/s  avg {sum(window)/len(window):.3f}  n={len(window)}')     # comment me out later
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
