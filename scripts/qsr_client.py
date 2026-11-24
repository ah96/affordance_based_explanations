#!/usr/bin/env python3
"""
ROS 2 client of the QSR service, for testing and demonstration.

Sends an angle to the ``qsr`` service and prints the qualitative spatial
relation that the server returns.

Usage
-----
    ros2 run affordance_based_explanations qsr_client.py <angle in radians>

Example
-------
    ros2 run affordance_based_explanations qsr_client.py 1.57
    1.5700 rad -> front
"""

import sys

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args

from affordance_based_explanations.srv import QSRService


def main():
    args = remove_ros_args(sys.argv)
    if len(args) != 2:
        print(f"Usage: {args[0]} <angle in radians>")
        return 1
    angle = float(args[1])

    rclpy.init()
    node = Node('qsr_client')
    client = node.create_client(QSRService, 'qsr')
    try:
        while not client.wait_for_service(timeout_sec=1.0):
            node.get_logger().info('Waiting for the qsr service.')
        request = QSRService.Request()
        request.angle = angle
        future = client.call_async(request)
        rclpy.spin_until_future_complete(node, future)
        print(f"{angle:.4f} rad -> {future.result().value}")
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
