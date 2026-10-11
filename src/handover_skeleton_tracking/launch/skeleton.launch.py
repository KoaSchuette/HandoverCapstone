from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, UnsetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # A leftover FASTDDS_BUILTIN_TRANSPORTS=LARGE_DATA in the terminal stops
    # these nodes from talking to the camera, so clear it for everything below.
    clear_transports = UnsetEnvironmentVariable('FASTDDS_BUILTIN_TRANSPORTS')

    # Same as: ros2 launch handover_realsense realsense.launch.py
    realsense = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [FindPackageShare('handover_realsense'), 'launch', 'realsense.launch.py']))
    )

    # Same as: ros2 run handover_skeleton_tracking skeleton_node
    # The node loads models/yolo26n-pose.pt relative to the current folder,
    # so launch this from the repo root.
    skeleton = Node(
        package='handover_skeleton_tracking',
        executable='skeleton_node',
        output='screen'
    )

    # rviz2, loading the saved config (markers + colour image)
    rviz_config = PathJoinSubstitution(
        [FindPackageShare('handover_skeleton_tracking'), 'rviz', 'skeleton.rviz']
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        clear_transports,
        realsense,
        skeleton,
        rviz,
    ])
