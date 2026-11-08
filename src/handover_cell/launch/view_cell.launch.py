"""Quick look at the cell in RViz only (no Gazebo, no MoveIt).

    ros2 launch handover_cell view_cell.launch.py

Opens a slider window for each arm joint. Good for checking the model and
reach without waiting for the physics sim to start.
"""
from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    description = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name="xacro")]), " ",
            PathJoinSubstitution([FindPackageShare("handover_cell"), "urdf", "handover_cell.urdf.xacro"]),
            " ur_type:=ur5e name:=ur",
        ]),
        value_type=str,
    )
    return LaunchDescription([
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[{"robot_description": description}]),
        Node(package="joint_state_publisher_gui", executable="joint_state_publisher_gui"),
        Node(package="rviz2", executable="rviz2",
             arguments=["-d", PathJoinSubstitution([FindPackageShare("ur_description"), "rviz", "view_robot.rviz"])]),
    ])
