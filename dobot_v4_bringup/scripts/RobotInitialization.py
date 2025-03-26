#!/usr/bin/env python3

import rosnode
import rospy
import sys
import copy
import rospkg
from std_msgs.msg import String
import dobot_v4_bringup.srv
import time
from dobot_v4_bringup.srv import ClearErrorRequest, EnableRobotRequest
import os

#Creating the ros node and service client

def EnableRobot():
    time.sleep(2)
    clear_error_service = rospy.ServiceProxy(clearErrorServiceName, dobot_v4_bringup.srv.ClearError)

    clear_error_response = clear_error_service()
    if(clear_error_response.res == 0):
        time.sleep(2)
        enable_robot_service = rospy.ServiceProxy(enableRobotServiceName, dobot_v4_bringup.srv.EnableRobot)
        enable_robot_response = enable_robot_service()
        if (enable_robot_response.res != 0):
            EnableRobot()
    else:
        EnableRobot()

if __name__ == '__main__':
    rospy.init_node("dobot_arm_enabler")
    nameSpace = os.environ['ROS_NAMESPACE'].split("/")[1]
    dobotType = os.environ['dobotType']+"_robot"

    clearErrorServiceName = "/" + nameSpace + "/" + dobotType + "/dobot_v4_bringup/srv/ClearError"
    enableRobotServiceName = "/" + nameSpace + "/" + dobotType + "/dobot_v4_bringup/srv/EnableRobot"

    rospy.wait_for_service(clearErrorServiceName)
    rospy.wait_for_service(enableRobotServiceName)
    EnableRobot()
