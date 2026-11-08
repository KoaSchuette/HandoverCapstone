import rclpy
import leap
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from hand_msgs.msg import Hand
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, Vector3, Quaternion

MM_TO_M = 1 / 1000  # Leap reports distances in mm, ROS expects m


def to_point(v, scale=MM_TO_M):
    return Point(x=v.x * scale, y=v.y * scale, z=v.z * scale)


def to_vector3(v, scale=1.0):
    return Vector3(x=v.x * scale, y=v.y * scale, z=v.z * scale)


def to_quaternion(q):
    return Quaternion(x=q.x, y=q.y, z=q.z, w=q.w)


class LeapPublisher(Node):

    def __init__(self):
        super().__init__('leap_publisher')
        self.left_hand = self.create_publisher(Hand, '/hand/left', 10)
        self.right_hand = self.create_publisher(Hand, '/hand/right', 10)
        self.hand_markers = self.create_publisher(MarkerArray,'/hand/markers', 10)

class LeapListener(leap.Listener):
    def __init__(self, node):
        super().__init__()
        self.node = node

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")
    def make_marker(self, msg, marker_array):
        line = Marker()
        marker = Marker()

        marker.type = Marker.SPHERE_LIST
        marker.action = Marker.ADD
        line.type = Marker.LINE_LIST 
        line.action = Marker.ADD

        marker.header = msg.header
        line.header = msg.header

        marker.scale.x = 0.01
        marker.scale.y = 0.01
        marker.scale.z = 0.01
        line.scale.x = 0.002
        line.scale.y = 0.002
        line.scale.z = 0.002

        marker.lifetime.sec = 0
        marker.lifetime.nanosec = 100000000
        line.lifetime = marker.lifetime
        if msg.handedness == Hand.LEFT:
            marker.ns = 'left_hand'
            line.ns = 'left_hand_lines'
            marker.color.r = 0.0
            marker.color.g = 1.0
            marker.color.b = 0.0
            marker.color.a = 1.0
        else:
            marker.ns = 'right_hand'
            line.ns = 'right_hand_lines'
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 1.0
        line.color = marker.color
        marker.id = 0
        line.id = 1
        marker.points.append(msg.palm_pose.position)
        for i in range(len(msg.fingers)):
            for j in range(len(msg.fingers[i].prev_joint)):
                marker.points.append(msg.fingers[i].prev_joint[j])
                line.points.append(msg.fingers[i].prev_joint[j])
                line.points.append(msg.fingers[i].next_joint[j])
            marker.points.append(msg.fingers[i].next_joint[3])

    
        marker_array.markers.append(marker)
        marker_array.markers.append(line)
        return marker_array

    def grab_data(self, hand, msg):
        msg.header.frame_id = "leap_link"
        msg.header.stamp = self.node.get_clock().now().to_msg()

        # Scalars
        msg.confidence = hand.confidence
        msg.grab_strength = hand.grab_strength
        msg.pinch_strength = hand.pinch_strength

        # Palm
        palm = hand.palm
        msg.palm_normal = to_vector3(palm.normal)
        msg.palm_direction = to_vector3(palm.direction)
        msg.palm_velocity = to_vector3(palm.velocity, MM_TO_M)  # mm/s -> m/s
        msg.palm_width = palm.width * MM_TO_M
        msg.palm_pose.position = to_point(palm.position)
        msg.palm_pose.orientation = to_quaternion(palm.orientation)

        # Arm
        msg.wrist_joint = to_point(hand.arm.next_joint)
        msg.elbow_joint = to_point(hand.arm.prev_joint)

        # Fingers: thumb, index, middle, ring, pinky
        # Bones: metacarpal, proximal, intermediate, distal
        for finger_msg, digit in zip(msg.fingers, hand.digits):
            for j, bone in enumerate(digit.bones):
                finger_msg.prev_joint[j] = to_point(bone.prev_joint)
                finger_msg.next_joint[j] = to_point(bone.next_joint)
                finger_msg.rotation[j] = to_quaternion(bone.rotation)
                finger_msg.width[j] = bone.width * MM_TO_M

    def on_tracking_event(self, event):
        # self.node.get_logger().info(f"Tracking event with {len(event.hands)} hands")
        marker_array = MarkerArray()
        for hand in event.hands:
            try:
                msg = Hand()
                if hand.type == leap.HandType.Left:
                    msg.handedness = Hand.LEFT
                    self.grab_data(hand,msg)
                    marker_array = self.make_marker(msg, marker_array)
                    self.node.left_hand.publish(msg)
                else:
                    msg.handedness = Hand.RIGHT
                    self.grab_data(hand,msg)
                    marker_array = self.make_marker(msg, marker_array)
                    self.node.right_hand.publish(msg)
            except Exception as e:
                self.node.get_logger().error(f"Failed to publish hand: {e!r}")
        
        self.node.hand_markers.publish(marker_array)
        
def main():
    rclpy.init()
    # Make Ros2 node leap publisher
    leap_publisher = LeapPublisher()
    # Create Listener to pull data from camera(NOT A ROS NODE)
    leap_listener = LeapListener(leap_publisher)

    connection = leap.Connection()
    connection.add_listener(leap_listener)


    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        try:
            rclpy.spin(leap_publisher)
        except(KeyboardInterrupt, ExternalShutdownException):
            pass


    
    leap_publisher.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
