import math

import cv2
import numpy as np
from ultralytics import YOLO

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
from message_filters import Subscriber, ApproximateTimeSynchronizer
from sensor_msgs.msg import Image, CameraInfo
from visualization_msgs.msg import Marker, MarkerArray
from skeleton_msgs.msg import Skeleton


# COCO skeleton: pairs of keypoint indices joined by a bone
SKELETON_BONES = [
    # legs
    (15, 13), (13, 11),   # left ankle → knee → hip
    (16, 14), (14, 12),   # right ankle → knee → hip
    # torso
    (11, 12),             # left hip → right hip
    (5, 11), (6, 12),     # shoulders → hips
    (5, 6),               # left shoulder → right shoulder
    # arms
    (5, 7), (7, 9),       # left shoulder → elbow → wrist
    (6, 8), (8, 10),      # right shoulder → elbow → wrist
    # face
    (1, 2),               # left eye → right eye
    (0, 1), (0, 2),       # nose → eyes
    (1, 3), (2, 4),       # eyes → ears
    (3, 5), (4, 6),       # ears → shoulders
]

class SkeletonNode(Node):
    def __init__(self):
        super().__init__('skeleton_node')
        #Starting variables
        self.camera_info = None
        #Load model
        self.model = YOLO("models/yolo26n-pose.pt")
        self.model.to('cuda')
        #Create cv bridge
        self.bridge = CvBridge()
        #pull camera intrinisics 
        self.info_sub = self.create_subscription(CameraInfo, 'camera/camera/color/camera_info', self.info_callback, qos_profile_sensor_data)
        # set up subs for camera data ---> call back function points to a synchronizer
        self.color_sub = Subscriber(self,Image,'camera/camera/color/image_raw', qos_profile=qos_profile_sensor_data)
        self.depth_sub = Subscriber(self,Image,'camera/camera/aligned_depth_to_color/image_raw',qos_profile=qos_profile_sensor_data)

        queue_size = 30
        max_delay = 0.01 #TBD
        self.image_depth_sync = ApproximateTimeSynchronizer([self.color_sub,self.depth_sub], queue_size, max_delay)
        self.image_depth_sync.registerCallback(self.SyncCallback)


        self.skeleton = self.create_publisher(Skeleton,'skeleton/position',10)
        self.skeleton_markers = self.create_publisher(MarkerArray,'/skeleton/markers', 10)

    def info_callback(self, msg):
        if self.camera_info is None:
            self.camera_info = msg
            self.get_logger().info(f'Intrinsics: fx={self.camera_info.k[0]:.1f} fy={self.camera_info.k[4]:.1f} cx={self.camera_info.k[2]:.1f} cy={self.camera_info.k[5]:.1f}')




    def make_marker(self,msg, marker_array):
        line = Marker()
        marker = Marker()

        marker.type = Marker.SPHERE_LIST
        marker.action = Marker.ADD
        line.type = Marker.LINE_LIST 
        line.action = Marker.ADD

        marker.header = msg.header
        line.header = msg.header

        marker.scale.x = 0.05
        marker.scale.y = 0.05
        marker.scale.z = 0.05
        line.scale.x = 0.01
        line.scale.y = 0.01
        line.scale.z = 0.01

        marker.lifetime.sec = 0
        marker.lifetime.nanosec = 100000000
        line.lifetime = marker.lifetime
        marker.ns = 'human_body'
        line.ns = 'human_body_lines'
        marker.color.r = 0.0
        marker.color.g = 0.0
        marker.color.b = 1.0
        marker.color.a = 1.0
        line.color = marker.color
        marker.id = 0
        line.id = 1
        for i in range(len(msg.keypoints)):
            if math.isnan(msg.keypoints[i].x):
                continue
            marker.points.append(msg.keypoints[i])

        for a, b in SKELETON_BONES:
            if math.isnan(msg.keypoints[a].x) or math.isnan(msg.keypoints[b].x):
                continue
            line.points.append(msg.keypoints[a])
            line.points.append(msg.keypoints[b])
        marker_array.markers.append(marker)
        marker_array.markers.append(line)
        return marker_array
    def SyncCallback(self, color, depth):
        marker_array = MarkerArray()
        msg = Skeleton()
        msg.header = color.header
        for keypoint in msg.keypoints:
            keypoint.x = float('nan')
            keypoint.y = float('nan')
            keypoint.z = float('nan')  
        if self.camera_info is None:
            return
        frame = self.bridge.imgmsg_to_cv2(color, desired_encoding='bgr8')
        depth_frame = self.bridge.imgmsg_to_cv2(depth, desired_encoding='passthrough')
        results = self.model.predict(frame,conf=0.6,device='cuda', verbose=False)
        r = results[0]
        if len(r) == 0:
            return
        keypoints = r.keypoints.data.cpu().numpy()
        for i, keypoint in enumerate(keypoints[0]):
            msg.confidence[i] = keypoint[2]
            if msg.confidence[i]< 0.5:
                continue
            u = int(round(keypoint[0])) # x in pixel space  
            v = int(round(keypoint[1])) # y in pixel space
            if not (0 <= u < self.camera_info.width and 0 <= v < self.camera_info.height):
                continue
            z = depth_frame[v,u]/1000 # z in camera space(real space)
            if z == 0:
                continue
            x =  (u - self.camera_info.k[2]) * z /self.camera_info.k[0]
            y =  (v - self.camera_info.k[5]) * z /self.camera_info.k[4]
            msg.keypoints[i].x = float(x)        
            msg.keypoints[i].y = float(y)
            msg.keypoints[i].z = float(z)
        self.skeleton.publish(msg)
        self.make_marker(msg,marker_array)
        self.skeleton_markers.publish(marker_array)




    


def main():
    rclpy.init()
    skeleton_node = SkeletonNode()

    try:
        rclpy.spin(skeleton_node)

    except KeyboardInterrupt:
        pass

    finally:
        skeleton_node.destroy_node()
        cv2.destroyAllWindows()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
