import time

import numpy as np

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class transcription_node:
    def __init__(self):
        super().__init__('leap_publisher')
        self.transcription = self.create_publisher(String, '/transcription', 10)