from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    # Static transform: rotates Leap's Y-up axes into ROS's Z-up
    leap_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--roll', '1.5708', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'world', '--child-frame-id', 'leap_link',
        ],
    )

    # TODO:same as ros2 run handover_hand_tracking leap_node
    leap = Node(
        package='handover_hand_tracking',
        executable='leap_node',
        output='screen'
    )

    # TODO: a Node for rviz2, loading saved config
    rviz_config = PathJoinSubstitution( #saved config
        [FindPackageShare('handover_hand_tracking'), 'rviz', 'hand_tracking.rviz']
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d',rviz_config]
    )


    return LaunchDescription([
        leap_tf,
        leap,
        rviz,
    ])