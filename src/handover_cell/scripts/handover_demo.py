#!/usr/bin/env python3
"""Handover demo: pegboard -> turn -> operator."""
import rclpy, math
from rclpy.node import Node
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint, MoveItErrorCodes

PICKUP = {
    "shoulder_pan_joint":    48.70,
    "shoulder_lift_joint": -117.97,
    "elbow_joint":          141.69,
    "wrist_1_joint":        -23.72,
    "wrist_2_joint":         48.70,
    "wrist_3_joint":          0,
}

HANDOVER = {
    "shoulder_pan_joint":  -104.86,
    "shoulder_lift_joint":  -63.27,
    "elbow_joint":           95.88,
    "wrist_1_joint":        -32.67,
    "wrist_2_joint":         75.16,
    "wrist_3_joint":          0,
}


class HandoverDemo(Node):
    def __init__(self):
        super().__init__("handover_demo")
        self.get_logger().info("Node started")
        self.client = ActionClient(self, MoveGroup, "move_action")

    def connect(self):
        self.get_logger().info("Waiting for move_group...")
        if not self.client.wait_for_server(timeout_sec=30.0):
            self.get_logger().error("No /move_action server found")
            return False
        self.get_logger().info("Connected to move_group")
        return True

    def make_goal(self, pose, speed=0.3):
        goal = MoveGroup.Goal()
        req = goal.request
        req.group_name = "ur_manipulator"
        req.start_state.is_diff = True
        req.pipeline_id = "pilz_industrial_motion_planner"
        req.planner_id = "PTP"
        req.allowed_planning_time = 5.0
        req.num_planning_attempts = 1
        req.max_velocity_scaling_factor = speed
        req.max_acceleration_scaling_factor = speed

        target = Constraints()
        for name, degrees in pose.items():
            target.joint_constraints.append(JointConstraint(
                joint_name=name, position=math.radians(degrees),
                tolerance_above=0.01, tolerance_below=0.01, weight=1.0))
        req.goal_constraints.append(target)

        goal.planning_options.plan_only = False
        return goal

    def send(self, goal):
        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error("move_group rejected the goal")
            return None
        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return result_future.result().result

def main():
    rclpy.init()
    node = HandoverDemo()
    if node.connect():
        for name, pose in [("pickup", PICKUP), ("handover", HANDOVER)]:
            result = node.send(node.make_goal(pose))
            code = result.error_code.val if result else None
            if code != MoveItErrorCodes.SUCCESS:
                print(name, "failed, error code", code)
                break
            end = result.planned_trajectory.joint_trajectory.points[-1].time_from_start
            print(f"{name}: {end.sec + end.nanosec * 1e-9:.2f} s")


if __name__ == "__main__":
    main()