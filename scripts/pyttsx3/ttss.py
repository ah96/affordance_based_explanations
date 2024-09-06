#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import pyttsx3

def tts_callback(msg):
    rospy.loginfo(f"Received text: {msg.data}")
    engine = pyttsx3.init()

    # Set properties for rate and volume
    rate = engine.getProperty('rate')   # Default rate is around 200
    engine.setProperty('rate', rate - 50)  # Lower value slows down the speech rate

    # Set properties for voice and adjust pitch if supported
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[2].id)  # Choose the first voice (usually the default)

    engine.say(msg.data)
    engine.runAndWait()

def tts_server():
    rospy.init_node('tts_server')
    rospy.Subscriber('tts_topic', String, tts_callback)
    rospy.loginfo("TTS Server is ready and waiting for text input...")
    rospy.spin()

if __name__ == '__main__':
    try:
        tts_server()
    except rospy.ROSInterruptException:
        pass
