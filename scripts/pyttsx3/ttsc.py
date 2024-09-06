#!/usr/bin/env python

import rospy
from std_msgs.msg import String

def tts_client():
    rospy.init_node('tts_client')
    pub = rospy.Publisher('tts_topic', String, queue_size=10)
    rate = rospy.Rate(1)  # 1 Hz

    while not rospy.is_shutdown():
        text_to_speak = input("Enter the text to speak: ")
        rospy.loginfo(f"Sending text: {text_to_speak}")
        pub.publish(text_to_speak)
        rate.sleep()

if __name__ == '__main__':
    try:
        tts_client()
    except rospy.ROSInterruptException:
        pass
