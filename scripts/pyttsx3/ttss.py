#!/usr/bin/env python3
"""
Offline text-to-speech server (ROS 2 node) with pyttsx3.

Speaks every string received on the topic ``tts_topic``.  pyttsx3 needs no
network connection, so the node also runs on a robot without internet access.

Topic
-----
tts_topic (std_msgs/msg/String), subscribed
    A message is spoken in full before the next one is taken.

To speak the textual explanations of the explanation node, remap the topic:

    ros2 run affordance_based_explanations ttss.py \
        --ros-args -r tts_topic:=textual_explanation

Voice
-----
The third voice of the engine is selected if there is one.  The voices depend
on the operating system and the installed speech engines.

Usage
-----
    ros2 run affordance_based_explanations ttss.py
"""

import pyttsx3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TtsServer(Node):

    def __init__(self):
        super().__init__('tts_server')
        self.subscription = self.create_subscription(
            String, 'tts_topic', self.speak, 10)
        self.get_logger().info('Offline TTS server ready on tts_topic.')

    def speak(self, msg):
        self.get_logger().info(f'Speaking: {msg.data}')

        # A new engine per message avoids state left over from the last call.
        engine = pyttsx3.init()

        # A lower rate than the default is easier to follow.
        engine.setProperty('rate', engine.getProperty('rate') - 50)

        voices = engine.getProperty('voices')
        if len(voices) > 2:
            engine.setProperty('voice', voices[2].id)

        engine.say(msg.data)
        engine.runAndWait()


def main():
    rclpy.init()
    node = TtsServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
