"""Gazebo + MoveIt + RViz with the full work cell.

    ros2 launch handover_cell cell_sim.launch.py

Reuses Universal Robots' ur_sim_moveit.launch.py, swapping in:
  - description_file   -> this package's arm + cell description
  - moveit_launch_file -> this package's MoveIt launch (cell-aware SRDF)
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    cell = FindPackageShare("handover_cell")
    return LaunchDescription([
        DeclareLaunchArgument("ur_type", default_value="ur5e"),
        DeclareLaunchArgument("safety_limits", default_value="true"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare("ur_simulation_gz"), "launch", "ur_sim_moveit.launch.py"])
            ),
            launch_arguments={
                "ur_type": LaunchConfiguration("ur_type"),
                "safety_limits": LaunchConfiguration("safety_limits"),
                "description_file": PathJoinSubstitution([cell, "urdf", "handover_cell.urdf.xacro"]),
                "moveit_launch_file": PathJoinSubstitution([cell, "launch", "cell_moveit.launch.py"]),
            }.items(),
        ),
    ])
