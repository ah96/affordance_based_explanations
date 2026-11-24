#!/usr/bin/env python3
"""
Text-to-speech on a PAL Robotics robot (ROS 2 action client).

Sends an explanation string to the speech synthesis of the robot as a goal of
the action type ``tts_msgs/action/TTS``.  Its goal has the fields ``input``
(the text), ``locale`` (for example ``en_GB``) and ``voice``.

Requirements
------------
- The package ``tts_msgs`` (https://github.com/pal-robotics/tts_msgs).
- A robot that offers an action server of this type.  The name of the action
  is the parameter ``action_name``.  Its default ``tts_engine/tts`` was not
  confirmed on a robot.  ``ros2 action list -t`` shows the name on the robot.

This node replaces the ROS 1 version, which published
``pal_interaction_msgs/TtsActionGoal`` on ``/tts/goal``.  It was not run on a
robot.

Usage
-----
    ros2 run affordance_based_explanations tts_tiago.py "Hello, this is TIAGo."
    ros2 run affordance_based_explanations tts_tiago.py "Hello." \
        --ros-args -p action_name:=tts_engine/tts -p locale:=en_GB
"""

import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.utilities import remove_ros_args

from tts_msgs.action import TTS


def main():
    args = remove_ros_args(sys.argv)
    text = ' '.join(args[1:]) or 'Hello, this is TIAGo speaking!'

    rclpy.init()
    node = Node('tts_tiago')
    action_name = node.declare_parameter('action_name', 'tts_engine/tts').value
    locale = node.declare_parameter('locale', 'en_GB').value

    client = ActionClient(node, TTS, action_name)
    status = 0
    try:
        if not client.wait_for_server(timeout_sec=5.0):
            node.get_logger().error(f'No action server "{action_name}".')
            status = 1
        else:
            goal = TTS.Goal()
            goal.input = text
            goal.locale = locale
            node.get_logger().info(f'Speaking: {text}')
            goal_future = client.send_goal_async(goal)
            rclpy.spin_until_future_complete(node, goal_future)
            goal_handle = goal_future.result()
            if not goal_handle.accepted:
                node.get_logger().error('The goal was rejected.')
                status = 1
            else:
                result_future = goal_handle.get_result_async()
                rclpy.spin_until_future_complete(node, result_future)
                error = result_future.result().result.error_msg
                if error:
                    node.get_logger().error(error)
                    status = 1
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    return status


if __name__ == '__main__':
    sys.exit(main())
