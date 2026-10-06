import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

import cv2
from cv_bridge import CvBridge


# ---------------------------------------------------------
# Debug visualization
# Set True to display the corresponding camera stream.
# ---------------------------------------------------------
DISPLAY_COLOR = True
DISPLAY_DEPTH = True


class RawMonitor(Node):

    def __init__(self):
        super().__init__('raw_monitor')
        self.bridge = CvBridge()
        self.counts = {'color': 0, 'depth': 0}
        self.seen = {'color': False, 'depth': False}

        ns = 'camera/camera'

        self.color_sub = self.create_subscription(
            Image,
            f'{ns}/color/image_raw',
            self.color_callback,
            qos_profile_sensor_data)

        self.depth_sub = self.create_subscription(
            Image,
            f'{ns}/depth/image_rect_raw',
            self.depth_callback,
            qos_profile_sensor_data)

        self.timer = self.create_timer(2.0, self.report)

    def color_callback(self, msg):
        self.bump('color', msg)

        if DISPLAY_COLOR:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            cv2.imshow('RealSense Color', frame)
            cv2.waitKey(1)


    def depth_callback(self, msg):
        self.bump('depth', msg)

        if DISPLAY_DEPTH:
            depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            # Scale depth image for visualization.
            depth_display = cv2.convertScaleAbs(depth, alpha=0.03)
            cv2.imshow('RealSense Depth', depth_display)
            cv2.waitKey(1)


    def bump(self, key, msg):
        if not self.seen[key]:
            self.get_logger().info(
                f'first {key}: '
                f'{msg.width}x{msg.height} '
                f'{msg.encoding} '
                f'frame_id={msg.header.frame_id}'
            )

            self.seen[key] = True

        self.counts[key] += 1


    def report(self):
        rates = {
            k: v / 2.0
            for k, v in self.counts.items()
        }

        self.get_logger().info(
            'Hz  color={color:.1f}  depth={depth:.1f}'.format(**rates)
        )

        self.counts = {
            k: 0
            for k in self.counts
        }


def main():
    rclpy.init()
    node = RawMonitor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        cv2.destroyAllWindows()

        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()