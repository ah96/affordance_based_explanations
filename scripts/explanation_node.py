#!/usr/bin/env python3
"""
ROS 2 node that generates affordance-based explanations (Algorithm 1).

The node follows the explanation generation framework of the paper (Fig. 6).
When the robot state is a planning failure or a trajectory deviation, it
scans the neighbourhood of the robot, consults the ontology, generates the
core explanation by replanning, and passes it to the Visualizer and the
Verbalizer.

Detection of failures and deviations is outside the scope of the paper and
is simulated: the state arrives on the topic ``robot_state``.

Subscribed topics
-----------------
robot_state (std_msgs/msg/String)
    "normal", "failure" or "deviation".
amcl_pose (geometry_msgs/msg/PoseWithCovarianceStamped)
    Pose of the robot in the map frame.
goal_pose (geometry_msgs/msg/PoseStamped)
    Goal of the navigation.
plan (nav_msgs/msg/Path)
    Global path of the navigation stack.  The last path received while the
    state is "normal" is the original path of the robot.  Without it, the
    node plans the original path itself.

Published topics
----------------
textual_explanation (std_msgs/msg/String)
    Published every ``period`` seconds while the state is a failure or a
    deviation, and on every call of the service.
explanation_layer (visualization_msgs/msg/MarkerArray)
    The visual explanation for RViz: one box per object near the robot, red
    for a cause and light gray otherwise.

Service
-------
explain (std_srvs/srv/Trigger)
    Generates and publishes an explanation now.  The response message holds
    the textual explanation.

Parameters
----------
ontology_file, map_info_file (string)   default: the library environment
explanation_type (string)   "descriptive", "suggestive" or "counterfactual"
task (string)               what the robot is doing, for example "fetch a book"
period (double)             seconds between two periodic explanations
neighborhood_radius, robot_radius, view_radius (double)   metres
image_file (string)         if set, the visual explanation is saved there

Usage
-----
    ros2 run affordance_based_explanations explanation_node.py
    ros2 topic pub --once robot_state std_msgs/msg/String "{data: deviation}"
    ros2 service call explain std_srvs/srv/Trigger
"""

import math

import rclpy
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Path
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from visualization_msgs.msg import Marker, MarkerArray

from aff import (AffordanceOntology, CoreExplanationGenerator, RobotState,
                 package_path)
from planner import GridMap
from qsr import QSR
from verbalize import verbalize_explanation
from visualize import COLOR_CAUSE, VisualExplanationGenerator

#: Height in metres of the boxes of the explanation layer in RViz.
MARKER_HEIGHT = 0.5


def yaw_of(orientation):
    """Return the yaw angle of a quaternion message."""
    return math.atan2(
        2.0 * (orientation.w * orientation.z + orientation.x * orientation.y),
        1.0 - 2.0 * (orientation.y ** 2 + orientation.z ** 2))


class ExplanationNode(Node):

    def __init__(self):
        super().__init__('explanation_node')
        library = ('ontologies', 'library')
        ontology_file = self.declare_parameter(
            'ontology_file', package_path(*library, 'ontology.csv')).value
        map_info_file = self.declare_parameter(
            'map_info_file', package_path(*library, 'map_info.csv')).value
        self.declare_parameter('explanation_type', 'counterfactual')
        self.declare_parameter('task', '')
        self.declare_parameter('image_file', '')
        period = self.declare_parameter('period', 5.0).value
        neighborhood_radius = self.declare_parameter(
            'neighborhood_radius', 3.0).value
        robot_radius = self.declare_parameter('robot_radius', 0.3).value
        view_radius = self.declare_parameter('view_radius', 3.0).value

        self.ontology = AffordanceOntology(ontology_file)
        self.generator = CoreExplanationGenerator(
            self.ontology, GridMap.from_map_info(map_info_file),
            neighborhood_radius=neighborhood_radius, robot_radius=robot_radius)
        self.visualizer = VisualExplanationGenerator(
            self.ontology, view_radius=view_radius, robot_radius=robot_radius)
        # The modified single-cross calculus of the paper.
        self.qsr = QSR(binary_qsr_choice=2, ternary_qsr_choice=2, R=1.0)

        self.state = RobotState.NORMAL
        self.robot_pose = None
        self.goal = None
        self.frame_id = 'map'
        self.original_path = None

        self.create_subscription(String, 'robot_state', self.on_state, 10)
        self.create_subscription(
            PoseWithCovarianceStamped, 'amcl_pose', self.on_pose, 10)
        self.create_subscription(PoseStamped, 'goal_pose', self.on_goal, 10)
        self.create_subscription(Path, 'plan', self.on_plan, 10)
        self.text_publisher = self.create_publisher(
            String, 'textual_explanation', 10)
        self.layer_publisher = self.create_publisher(
            MarkerArray, 'explanation_layer', 10)
        self.create_service(Trigger, 'explain', self.on_explain)
        self.create_timer(period, self.on_timer)
        self.get_logger().info(
            f'Explanation node ready, {len(self.ontology.objects)} objects '
            f'in the ontology.')

    # ------------------------------------------------------------------
    # Inputs
    # ------------------------------------------------------------------

    def on_state(self, msg):
        try:
            self.state = RobotState(msg.data.strip().lower())
        except ValueError:
            self.get_logger().warn(f'Unknown robot state "{msg.data}".')

    def on_pose(self, msg):
        pose = msg.pose.pose
        self.robot_pose = (pose.position.x, pose.position.y,
                           yaw_of(pose.orientation))
        self.frame_id = msg.header.frame_id or self.frame_id

    def on_goal(self, msg):
        self.goal = (msg.pose.position.x, msg.pose.position.y)

    def on_plan(self, msg):
        # A path planned after the failure or deviation is not the original one.
        if self.state == RobotState.NORMAL and msg.poses:
            self.original_path = [
                (p.pose.position.x, p.pose.position.y) for p in msg.poses]

    # ------------------------------------------------------------------
    # Algorithm 1
    # ------------------------------------------------------------------

    def explain(self):
        """Run one pass of Algorithm 1.  Returns (success, text)."""
        if self.state not in (RobotState.FAILURE, RobotState.DEVIATION):
            return False, 'The robot state is normal, nothing to explain.'
        if self.robot_pose is None or self.goal is None:
            return False, 'No robot pose or no goal received yet.'

        core = self.generator.generate(
            self.robot_pose, self.goal, self.state, self.original_path)
        if not core:
            return False, 'No object near the robot explains the robot state.'

        explanation_type = self.get_parameter('explanation_type').value
        task = self.get_parameter('task').value or None
        try:
            text = verbalize_explanation(
                core, self.ontology, self.qsr, explanation_type, task)
        except KeyError:
            return False, f'Unknown explanation type "{explanation_type}".'

        self.text_publisher.publish(String(data=text))
        self.layer_publisher.publish(self.explanation_layer(core))
        image_file = self.get_parameter('image_file').value
        if image_file:
            self.visualizer.generate(core, output_path=image_file)
        return True, text

    def on_timer(self):
        success, text = self.explain()
        if success:
            self.get_logger().info(text)

    def on_explain(self, request, response):
        response.success, response.message = self.explain()
        return response

    def explanation_layer(self, core):
        """Return the visual explanation as markers for RViz."""
        layer = MarkerArray()
        clear = Marker()
        clear.header.frame_id = self.frame_id
        clear.action = Marker.DELETEALL
        layer.markers.append(clear)
        stamp = self.get_clock().now().to_msg()
        for index, (label, color) in enumerate(
                self.visualizer.colors(core).items()):
            obj = self.ontology.objects[label]
            marker = Marker()
            marker.header.frame_id = self.frame_id
            marker.header.stamp = stamp
            marker.ns = 'explanation_layer'
            marker.id = index
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = obj['x']
            marker.pose.position.y = obj['y']
            marker.pose.position.z = MARKER_HEIGHT / 2.0
            marker.pose.orientation.w = 1.0
            marker.scale.x = obj['w']
            marker.scale.y = obj['h']
            marker.scale.z = MARKER_HEIGHT
            marker.color.r, marker.color.g, marker.color.b = color
            marker.color.a = 1.0 if color == COLOR_CAUSE else 0.6
            layer.markers.append(marker)
        return layer


def main():
    rclpy.init()
    node = ExplanationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
