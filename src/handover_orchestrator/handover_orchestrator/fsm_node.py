from enum import Enum, auto
import threading

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from std_srvs.srv import Trigger
from handover_interfaces.msg import Hand, Skeleton
from handover_interfaces.srv import RackPickupTrigger


class State(Enum):
    IDLE = auto()
    RACK_PICK_UP = auto()
    WAIT_FOR_HAND = auto()
    HANDOVER = auto()
    RELEASE = auto()
    RETURN = auto()


class Fsm_node(Node):
    def __init__(self):
        super().__init__("fsm_node")
        self.state = State.IDLE
        self.state_lock = threading.Lock()
        self.latest_hand = None

        #mark these variables almost like mutexs
        self.srv_group = MutuallyExclusiveCallbackGroup()
        self.tick_group = MutuallyExclusiveCallbackGroup()

        # Define server triggers:   
        # SLM Service
        self.srv = self.create_service(RackPickupTrigger, 'tool_request', self.tool_request_callback,callback_group=self.srv_group)

        # # to start the handover seqence
        # self.start_cli = self.create_client(Trigger, 'start_handover', callback_group=self.srv)
        # while not self.start_cli.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('start_handover service not available, waiting...')

        # # to stop the handover seqence
        # self.stop_cli = self.create_client(Trigger, 'stop_handover',  callback_group=self.srv)
        # while not self.stop_cli.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('stop_handover service not available, waiting...')

        # #hand subscriber
        # self.hand_sub = self.create_subscription(Hand, '/right/hand',self.hand_callback, 10)
        # #heart beat timer runs a tick callback every 0.1s
        # self.timer = self.create_timer(0.1, self.tick, callback_group=self.tick_group)


    # Tool request callback, called when a tool request is received from the LLM
    def tool_request_callback(self, request, response):
        Req = RackPickupTrigger.Request
        with self.state_lock:
            if request.function == Req.FUNCTION_DELIVER_TOOL:
                if request.subject not in (Req.SUBJECT_RED, Req.SUBJECT_GREEN, Req.SUBJECT_BLUE):
                    response.success = False
                    response.message = f'Invalid subject {request.subject}.'
                elif self.state == State.IDLE:
                    self.get_logger().info(f'Tool request received: subject {request.subject}, starting rack pickup sequence.')
                    self.state = State.RACK_PICK_UP
                    response.success = True
                    response.message = 'Tool request accepted, starting rack pickup sequence.'
                else:
                    self.get_logger().info(f'Tool request received, but robot in state {self.state.name}, rejecting request.')
                    response.success = False
                    response.message = f'Tool request rejected, robot in state {self.state.name}.'
            elif request.function in (Req.FUNCTION_CANCEL_TASK, Req.FUNCTION_PAUSE_TASK, Req.FUNCTION_RESUME_TASK):
                self.get_logger().info(f'Command {request.function} received (not implemented yet).')
                response.success = False
                response.message = 'Command recognised but not implemented yet.'
            else:
                response.success = False
                response.message = f'Unknown function {request.function}.'
        return response


def main():
    print('Hi from handover_orchestrator.')
    rclpy.init()
    node = Fsm_node()
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
