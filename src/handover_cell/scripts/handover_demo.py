#!/usr/bin/env python3
"""Handover demo: pegboard -> turn -> operator."""
import rclpy, math, os
from rclpy.node import Node
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint, MoveItErrorCodes
from datetime import datetime



HANDOVER = {
    "shoulder_pan_joint":  -104.86,
    "shoulder_lift_joint":  -63.27,
    "elbow_joint":           95.88,
    "wrist_1_joint":        -32.67,
    "wrist_2_joint":         75.16,
    "wrist_3_joint":          0,
}

CSV = "cycle_times.csv"
SPEED = 0.3
PLANNER = "PTP"

PICKUPS = {
    -0.05: [30.60, -134.48, 147.09, -12.61, 30.60, 0],
     0.00: [48.70, -117.97, 141.69, -23.72, 48.70, 0],
     0.05: [57.72, -106.75, 135.63, -28.87, 57.72, 0],
     0.10: [63.37,  -97.79, 129.04, -31.26, 63.37, 0],
     0.15: [67.30,  -90.08, 122.01, -31.93, 67.30, 0],
}

def bottleneck(traj):
    start = traj.points[0].positions
    end = traj.points[-1].positions
    moves = [abs(b - a) for a, b in zip(start, end)]
    i = moves.index(max(moves))
    return traj.joint_names[i].replace("_joint", ""), math.degrees(moves[i])

def log_row(offset, leg, status, t="", joint="", deg="", plan_t=""):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(CSV):
        with open(CSV, "w") as f:
            f.write("timestamp,offset_m,leg,status,time_s,speed_scale,planner," "bottleneck_joint,bottleneck_deg,planning_time_s\n")
    with open(CSV, "a") as f:
        f.write(f"{stamp},{offset},{leg},{status},{t},{SPEED},{PLANNER},{joint},{deg},{plan_t}\n")

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

    def make_goal(self, pose, speed=SPEED):
        goal = MoveGroup.Goal()
        req = goal.request
        req.group_name = "ur_manipulator"
        req.start_state.is_diff = True
        req.pipeline_id = "pilz_industrial_motion_planner"
        req.planner_id = PLANNER
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
    offset = round(float(os.environ.get("PEGBOARD_OFFSET", "0")), 2)

    if offset not in PICKUPS:
        print(f"offset {offset}: no pickup angles, pickup is unreachable")
        log_row(offset, "pickup", "unreachable")                          # ◄ 1
        return

    pickup = dict(zip(HANDOVER.keys(), PICKUPS[offset]))
    rclpy.init()
    node = HandoverDemo()
    if node.connect():
        for name, pose in [("pickup", pickup), ("handover", HANDOVER), ("return", pickup)]:
            result = node.send(node.make_goal(pose))
            code = result.error_code.val if result else None
            if code != MoveItErrorCodes.SUCCESS:
                print(name, "failed, error code", code)
                log_row(offset, name, f"failed {code}")                   # ◄ 2
                break
            traj = result.planned_trajectory.joint_trajectory             # ◄ 3 (from here…
            end = traj.points[-1].time_from_start
            t = end.sec + end.nanosec * 1e-9
            joint, deg = bottleneck(traj)
            print(f"{name}: {t:.2f} s  (slowest: {joint}, {deg:.1f} deg)")
            log_row(offset, name, "SUCCESS", f"{t:.3f}", joint, f"{deg:.1f}",
                    f"{result.planning_time:.3f}")                         #      …to here)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()