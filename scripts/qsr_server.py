#!/usr/bin/env python3
"""
ROS 2 service node for the Qualitative Spatial Reasoning (QSR) calculus.

Other nodes ask this service for the qualitative spatial relation of an
object to the robot, so that they do not need the QSR code themselves.

Service
-------
qsr (affordance_based_explanations/srv/QSRService)
    Request:  float64 angle   angle of the object in radians, in the frame of
                              the binary calculi (0 = right, +pi/2 = front)
    Response: string value    "front", "back", "left" or "right"

The node uses the modified single-cross calculus of the paper
(``binary_qsr_choice=2``).

Usage
-----
    ros2 run affordance_based_explanations qsr_server.py
"""

import rclpy
from rclpy.node import Node

from affordance_based_explanations.srv import QSRService
from qsr import QSR


class QsrServer(Node):

    def __init__(self):
        super().__init__('qsr_server')
        # R is the close/distant threshold of ternary calculus 4, not used here.
        self.qsr = QSR(binary_qsr_choice=2, ternary_qsr_choice=2, R=1.0)
        self.service = self.create_service(QSRService, 'qsr', self.handle_qsr)
        self.get_logger().info('QSR service ready: left, right, front, back.')

    def handle_qsr(self, request, response):
        response.value = self.qsr.getBinaryQsrValue(request.angle)
        self.get_logger().debug(f'angle {request.angle:.3f} -> {response.value}')
        return response


def main():
    rclpy.init()
    node = QsrServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
