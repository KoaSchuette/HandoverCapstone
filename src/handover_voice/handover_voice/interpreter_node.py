import time

import numpy as np
from std_msgs.msg import String

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup

from handover_interfaces.srv import RackPickupTrigger
from handover_voice.command_parser import parse_command
from handover_voice.commands import Controller, FUNCTION_CODES, SUBJECT_CODES


class Interpreter_node(Node):
    def __init__(self):
        super().__init__('interpreter_node')
        self.srv_group = MutuallyExclusiveCallbackGroup()

        self.controller = Controller()

        # SLM Client
        self.cli = self.create_client(RackPickupTrigger, 'tool_request', callback_group=self.srv_group)
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        self.script_sub = self.create_subscription(String, '/transcription', self.transcript_callback, 10)



        try:
            parse_command("warm up")   # first call loads the model;
        except Exception as e:
            self.get_logger().error(f"Error warming up command parser: {e}")

    def transcript_callback(self, msg):
        text = msg.data
        try:
            cmd, secs = parse_command(text)
        except Exception as e:
            self.get_logger().error(f"parse_command failed (is Ollama running?): {e}")
            return
        result = self.controller.handle(cmd, text)
        self.get_logger().info(f"Command: {cmd}, Time: {secs:.2f}s, Result: {result}")

        if result is None:
            self.get_logger().info("Command ignored (voice inactive).")
            return

        function_code, subject_code = result
        if function_code == FUNCTION_CODES["deliver_tool"]:
            request = RackPickupTrigger.Request()
            request.function = function_code
            request.subject = subject_code
            future = self.cli.call_async(request)
            future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Service response: success={response.success}, message='{response.message}'")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")



def main():
    rclpy.init()
    node = Interpreter_node()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
