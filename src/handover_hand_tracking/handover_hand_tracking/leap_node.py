import rclpy
import leap
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import Marker, MarkerArray

class LeapPublisher(Node):

    def __init__(self):
        super().__init__('leap_publisher')
        self.palm_pose_left = self.create_publisher(PoseStamped, '/hand/left/palm_pose', 10)
        self.palm_pose_right = self.create_publisher(PoseStamped, '/hand/right/palm_pose', 10)
        

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

    def on_tracking_event(self, event):
        # self.node.get_logger().info(f"Tracking event with {len(event.hands)} hands")
        for hand in event.hands:
            try:
                msg = PoseStamped()
                if hand.type == leap.HandType.Left:
                    msg.header.frame_id = "leap_link"
                    msg.header.stamp = self.node.get_clock().now().to_msg() 
                    msg.pose.position.x = hand.palm.position.x/1000 #output in mm so converted to m
                    msg.pose.position.y = hand.palm.position.y/1000
                    msg.pose.position.z = hand.palm.position.z/1000 
                    msg.pose.orientation.x = hand.palm.orientation.x
                    msg.pose.orientation.y = hand.palm.orientation.y
                    msg.pose.orientation.z = hand.palm.orientation.z
                    msg.pose.orientation.w = hand.palm.orientation.w
                    self.node.palm_pose_left.publish(msg)
                else:
                    msg.header.frame_id = "leap_link"
                    msg.header.stamp = self.node.get_clock().now().to_msg() 
                    msg.pose.position.x = hand.palm.position.x/1000
                    msg.pose.position.y = hand.palm.position.y/1000
                    msg.pose.position.z = hand.palm.position.z/1000
                    msg.pose.orientation.x = hand.palm.orientation.x
                    msg.pose.orientation.y = hand.palm.orientation.y
                    msg.pose.orientation.z = hand.palm.orientation.z
                    msg.pose.orientation.w = hand.palm.orientation.w
                    self.node.palm_pose_right.publish(msg)
            except Exception as e:
                self.node.get_logger().error(f"Failed to publish hand: {e!r}")
            

        
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
