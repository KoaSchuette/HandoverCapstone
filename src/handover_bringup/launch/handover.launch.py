"""Start the handover cell.

ros2 launch handover_bringup handover.launch.py mode:=mock
ros2 launch handover_bringup handover.launch.py mode:=real robot_ip:=<robot-ip>
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def include(package, launch_file, **kwargs):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [FindPackageShare(package), 'launch', launch_file])),
        **kwargs,
    )


def launch_setup(context):
    mode = LaunchConfiguration('mode').perform(context)
    robot_ip = LaunchConfiguration('robot_ip').perform(context)

    if mode == 'real' and not robot_ip:
        raise RuntimeError('mode:=real needs robot_ip:=<robot-ip>')

    # The UR driver runs in both modes. Only the hardware plugin changes,
    # so every node above it behaves the same on mock and real.
    robot = include(
        'ur_robot_driver', 'ur_control.launch.py',
        launch_arguments={
            'ur_type': 'ur5e',
            'robot_ip': robot_ip if mode == 'real' else '0.0.0.0',
            'use_mock_hardware': 'true' if mode == 'mock' else 'false',
            'description_file': PathJoinSubstitution(
                [FindPackageShare('handover_moveit_config'), 'config', 'workcell.urdf.xacro']),
            'launch_rviz': 'false',
        }.items(),
    )

    return [
        robot,
        include('handover_moveit_config', 'move_group.launch.py'),
        include('handover_moveit_config', 'moveit_rviz.launch.py',
                condition=IfCondition(LaunchConfiguration('use_rviz'))),
        Node(package='handover_motion', executable='planner_node', output='screen'),
        Node(package='handover_hand_tracking', executable='leap_node', output='screen',
             condition=IfCondition(LaunchConfiguration('use_leap'))),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('mode', default_value='mock', choices=['mock', 'real'],
                              description='mock runs without a robot, real moves the arm'),
        DeclareLaunchArgument('robot_ip', default_value='',
                              description='Robot IP address, required for mode:=real'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('use_leap', default_value='true',
                              description='Start the Ultraleap hand tracking node'),
        OpaqueFunction(function=launch_setup),
    ])

