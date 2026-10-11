import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    rs_launch = os.path.join(
        get_package_share_directory('realsense2_camera'), 'launch', 'rs_launch.py')

    return LaunchDescription([
        # Fast DDS's default shared-memory segment is smaller than one colour
        # frame, so most colour images were dropped (~3-20 Hz instead of 30).
        # This profile enlarges the segment to 16 MB and keeps UDP for other hosts.
        SetEnvironmentVariable(
            'FASTRTPS_DEFAULT_PROFILES_FILE',
            os.path.join(get_package_share_directory('handover_realsense'),
                         'config', 'fastdds_shm.xml')),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rs_launch),
            launch_arguments={
                'camera_name': 'camera',
                'camera_namespace': 'camera',
                # Matching depth + colour resolution makes alignment cheap.
                # Verify the parameter names with: ros2 launch realsense2_camera rs_launch.py --show-args
                'depth_module.depth_profile': '848x480x30',
                'rgb_camera.color_profile': '848x480x30',
                'align_depth.enable': 'true',
                # 'enable_gyro': 'true',
                # 'enable_accel': 'true',
                # 'unite_imu_method': '2',
                'pointcloud.enable': 'false',
            }.items(),
        )
    ])