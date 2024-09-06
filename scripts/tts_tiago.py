#!/usr/bin/env python

import rospy
from pal_interaction_msgs.msg import TtsActionGoal

def publish_tts_goal(text, lang_id='en_GB', voice_id='male', pitch=100):
    # Initialize the ROS node
    rospy.init_node('publisher_node', anonymous=False)

    # Create a publisher to the /tts/goal topic
    pub = rospy.Publisher('/tts/goal', TtsActionGoal, queue_size=1)

    embedded_text = f"<pitch level='{pitch}'>{text}</pitch>"

    # Create a TtsActionGoal message
    tts_goal = TtsActionGoal()
    tts_goal.goal.rawtext.text = text            # Text to speak
    tts_goal.goal.rawtext.lang_id = lang_id      # Language identifier (e.g., 'en_GB' for British English)
    #tts_goal.goal.rawtext.voice_id = voice_id    # Voice identifier (e.g., 'male' or 'female')

    #tts_goal.goal_id.id = "/pal_webcommander"

    tts_goal.goal.wait_before_speaking = 0.0      # Language identifier (e.g., 'en_GB' for British English)

    # Publish the TTS goal message
    rospy.loginfo(f"Publishing TTS goal: {text}")
    pub.publish(tts_goal)

    # Keep the node running until manually terminated
    #rospy.spin()

if __name__ == '__main__':
    try:
        # Example usage: Send text to be spoken
        for i in range(0, 10):
            publish_tts_goal("Hello, this is TIAGo speaking!", lang_id='en_GB', voice_id='male')
    except rospy.ROSInterruptException:
        pass
