from enum import Enum, auto
import threading

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from std_srvs.srv import Trigger
from hand_msgs.msg import Hand
from skeleton_msgs.msg import Skeleton


class State(Enum):
    IDLE = auto()
    PICK_UP = auto()
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
        self.service_group = MutuallyExclusiveCallbackGroup()
        self.tick_group = MutuallyExclusiveCallbackGroup()


        #define serives trigger to start and stop the handover seqence
        self.start_srv = self.create_service(Trigger, 'start_handover', self.start_callback, callback_group=self.service_group)
        self.stop_srv = self.create_service(Trigger, 'stop_handover', self.start_callback, callback_group=self.service_group)

        #hand subscriber
        self.hand_sub = self.create_subscription(Hand, '/right/hand',self.hand_callback, 10)
        #heart beat timer runs a tick callback every 0.1s
        self.timer = self.create_timer(0.1, self.tick, callback_group=self.tick_group)



def main():
    print('Hi from handover_orchestrator.')


if __name__ == '__main__':
    main()
