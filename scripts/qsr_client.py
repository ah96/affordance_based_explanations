#!/usr/bin/env python

from __future__ import print_function

import sys
import rospy
from affordance_based_explanations.srv import *

def qsr_client(angle):
    rospy.wait_for_service('qsr')
    try:
        qsr_get_binary = rospy.ServiceProxy('qsr', QSRService)
        resp1 = qsr_get_binary(angle)
        return resp1.value
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)

def usage():
    return "%s"%sys.argv[0]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        angle = float(sys.argv[1])
    else:
        print(usage())
        sys.exit(1)
    print("Requesting value for angle %s"%(angle))
    print("%s -> %s"%(angle, qsr_client(angle)))