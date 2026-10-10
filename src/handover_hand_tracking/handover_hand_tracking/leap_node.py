import rclpy
import leap
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from hand_msgs.msg import Hand
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import Marker, MarkerArray

class LeapPublisher(Node):

    def __init__(self):
        super().__init__('leap_publisher')
        self.left_hand = self.create_publisher(Hand, '/hand/left', 10)
        self.right_hand = self.create_publisher(Hand, '/hand/right', 10)
        

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


    def grab_data(self,hand,msg):
        msg.header.frame_id = "leap_link"
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.confidence = hand.confidence
        msg.grab_strength = hand.grab_strength
        msg.pinch_strength = hand.pinch_strength
        msg.palm_normal.x = hand.palm.normal.x
        msg.palm_normal.y = hand.palm.normal.y
        msg.palm_normal.z = hand.palm.normal.z
        msg.palm_direction.x = hand.palm.direction.x
        msg.palm_direction.y = hand.palm.direction.y
        msg.palm_direction.z = hand.palm.direction.z
        msg.palm_velocity.x = hand.palm.velocity.x/1000
        msg.palm_velocity.y = hand.palm.velocity.y/1000
        msg.palm_velocity.z = hand.palm.velocity.z/1000
        msg.palm_width = hand.palm.width/1000
        msg.palm.position.x = hand.palm.position.x/1000 #output in mm so converted to m
        msg.palm.position.y = hand.palm.position.y/1000
        msg.palm.position.z = hand.palm.position.z/1000 
        msg.palm.orientation.x = hand.palm.orientation.x
        msg.palm.orientation.y = hand.palm.orientation.y
        msg.palm.orientation.z = hand.palm.orientation.z
        msg.palm.orientation.w = hand.palm.orientation.w
        msg.wrist_joint.x = hand.arm.next_joint.x/1000
        msg.wrist_joint.y = hand.arm.next_joint.y/1000
        msg.wrist_joint.z = hand.arm.next_joint.z/1000
        msg.elbow_joint.x = hand.arm.prev_joint.x/1000
        msg.elbow_joint.y = hand.arm.prev_joint.y/1000
        msg.elbow_joint.z = hand.arm.prev_joint.z/1000
        for i in range(len(hand.digits)):
            for j in range(len(hand.digits[i].bones)):
                msg.fingers[i].prev_joint[j].x = hand.digits[i].bones[j].prev_joint.x/1000
                msg.fingers[i].prev_joint[j].y = hand.digits[i].bones[j].prev_joint.y/1000
                msg.fingers[i].prev_joint[j].z = hand.digits[i].bones[j].prev_joint.z/1000
                msg.fingers[i].next_joint[j].x = hand.digits[i].bones[j].next_joint.x/1000
                msg.fingers[i].next_joint[j].y = hand.digits[i].bones[j].next_joint.y/1000
                msg.fingers[i].next_joint[j].z = hand.digits[i].bones[j].next_joint.z/1000
                msg.fingers[i].rotation[j].x = hand.digits[i].bones[j].rotation.x
                msg.fingers[i].rotation[j].y = hand.digits[i].bones[j].rotation.y
                msg.fingers[i].rotation[j].z = hand.digits[i].bones[j].rotation.z
                msg.fingers[i].rotation[j].w = hand.digits[i].bones[j].rotation.w
                msg.fingers[i].width[j] = hand.digits[i].bones[j].width/1000

    def on_tracking_event(self, event):
        # self.node.get_logger().info(f"Tracking event with {len(event.hands)} hands")
        for hand in event.hands:
            try:
                msg = Hand()
                if hand.type == leap.HandType.Left:
                    msg.handedness = Hand.LEFT
                    self.grab_data(hand,msg)
                    self.node.left_hand.publish(msg)
                else:
                    msg.handedness = Hand.RIGHT
                    self.grab_data(hand,msg)
                    self.node.right_hand.publish(msg)
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
