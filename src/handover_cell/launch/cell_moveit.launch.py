"""MoveIt + RViz for the handover cell.

Same as ur_moveit_config/launch/ur_moveit.launch.py (Universal Robots, BSD-3),
except the SRDF comes from this package so MoveIt knows which cell/arm
collision pairs to ignore. Everything else (kinematics, joint limits, planners,
controllers) still comes from ur_moveit_config.
"""
import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")
    use_sim_time = LaunchConfiguration("use_sim_time")

    srdf = Path(get_package_share_directory("handover_cell")) / "srdf" / "handover_cell.srdf.xacro"
    moveit_config = (
        MoveItConfigsBuilder(robot_name="ur", package_name="ur_moveit_config")
        .robot_description_semantic(srdf, {"name": ur_type})
        .to_moveit_configs()
    )

    warehouse = {
        "warehouse_plugin": "warehouse_ros_sqlite::DatabaseConnection",
        "warehouse_host": os.path.expanduser("~/.ros/warehouse_ros.sqlite"),
    }

    # MoveIt reads the robot (arm + cell) from the /robot_description topic,
    # which ur_sim_control publishes from handover_cell.urdf.xacro.
    wait_robot_description = Node(
        package="ur_robot_driver",
        executable="wait_for_robot_description",
        output="screen",
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            warehouse,
            {"use_sim_time": use_sim_time, "publish_robot_description_semantic": True},
        ],
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", PathJoinSubstitution([FindPackageShare("ur_moveit_config"), "config", "moveit.rviz"])],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            warehouse,
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument("ur_type", default_value="ur5e"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        # accepted (and ignored) so ur_sim_moveit.launch.py can pass them in
        DeclareLaunchArgument("launch_rviz", default_value="true"),
        DeclareLaunchArgument("launch_servo", default_value="false"),
        wait_robot_description,
        RegisterEventHandler(OnProcessExit(target_action=wait_robot_description,
                                           on_exit=[move_group, rviz])),
    ])
