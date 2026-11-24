#!/usr/bin/env python3
"""
Offline text-to-speech client (ROS 2 node).

Reads lines of text from the terminal and publishes them on ``tts_topic``.
The server node ``ttss.py`` speaks them.

Usage
-----
    # Terminal 1
    ros2 run affordance_based_explanations ttss.py

    # Terminal 2: type the text to speak
    ros2 run affordance_based_explanations ttsc.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


def main():
    rclpy.init()
    node = Node('tts_client')
    publisher = node.create_publisher(String, 'tts_topic', 10)
    try:
        while rclpy.ok():
            text = input('Enter text to speak (Ctrl-C to quit): ')
            node.get_logger().info(f'Publishing: {text}')
            publisher.publish(String(data=text))
            # Lets the middleware deliver the message before the next prompt.
            rclpy.spin_once(node, timeout_sec=0.1)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
