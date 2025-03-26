#!/usr/bin/env python3

import rosnode
import rospy
import sys
import copy
import rospkg
import extend_msgs
from extend_msgs.msg import GripperControl, GripperResponse
from std_msgs.msg import Header
import dobot_v4_bringup.srv
import time
import gripper_global_variables
import os

from dobot_v4_bringup.srv import ModbusCreateRequest, SetHoldRegsRequest, ClearErrorRequest, EnableRobotRequest

def initialize():
    #Initialize the Modbus service and the response publisher
    pubGripperCommandRepublisher = rospy.Publisher('extend_gripper_republished_command',GripperControl,queue_size=1)
    pubGripperResponse = rospy.Publisher('extend_gripper_response',GripperResponse,queue_size=1)
    return pubGripperCommandRepublisher,pubGripperResponse

def dataCallback(msg):
    # Remaping Range [0,1] to [0,255]
    gripper_value = 255 * msg.gripperAnalog.data

    if(gripper_global_variables.gripper_data_count == 5):
        gripper_modbus_service = rospy.ServiceProxy(setHoldRegServiceName, dobot_v4_bringup.srv.SetHoldRegs)
        gripper_modbus_data = SetHoldRegsRequest()
        gripper_modbus_data.index = 0
        gripper_modbus_data.addr = 1000   # Register Adress 03E8
        gripper_modbus_data.count = 3     # Number of data to be sent
        gripper_modbus_data.valTab = "{2304," + str(gripper_value) + ",60000}" # {2304:Actuation, Value of the gripper: open/close, Speed of the gripper:0-65535}
        gripper_modbus_data.valType = "U16"  #Data format: 16-bit Unsigned integer type
        gripper_modbus_service(gripper_modbus_data)

        gripper_global_variables.gripper_data_count = 0
    else:
        gripper_global_variables.gripper_data_count += 1
    
    header = Header()
    header.seq = 0
    header.frame_id = ""
    header.stamp = rospy.Time.now()

    pubGripperCommandRepublisherData = GripperControl()
    pubGripperCommandRepublisherData = msg
    pubGripperCommandRepublisherData.header = header
    pubGripperCommandRepublisher.publish(pubGripperCommandRepublisherData)

    #Fetching the Gripper Response Joint States and Force
    pubGripperResponseData = GripperResponse()
    pubGripperResponseData.header = header
    pubGripperResponse.publish(pubGripperResponseData)


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


def InitializeGlobalVariables():
    gripper_global_variables.gripper_prev_state = 0
    gripper_global_variables.gripper_initialization = True
    gripper_global_variables.gripper_data_count = 0


if __name__ == '__main__':

    #Creating the ros node and service client
    rospy.init_node("robotiq_gripper")
    nameSpace = os.environ['ROS_NAMESPACE'].split("/")[1]
    dobotType = os.environ['dobotType']+"_robot"

    clearErrorServiceName = "/" + nameSpace + "/" + dobotType + "/dobot_v4_bringup/srv/ClearError"
    enableRobotServiceName = "/" + nameSpace + "/" + dobotType + "/dobot_v4_bringup/srv/EnableRobot"
    modbusCreateServiceName = "/" + nameSpace + "/" + dobotType + "/dobot_v4_bringup/srv/ModbusCreate"
    setHoldRegServiceName = "/" + nameSpace + "/" + dobotType + "/dobot_v4_bringup/srv/SetHoldRegs"


    rospy.wait_for_service(clearErrorServiceName)
    rospy.wait_for_service(enableRobotServiceName)
    rospy.wait_for_service(modbusCreateServiceName)
    rospy.wait_for_service(setHoldRegServiceName)


    InitializeGlobalVariables()
    (pubGripperCommandRepublisher,pubGripperResponse) = initialize()  
    #Configure the modbus
    modbus_create_service = rospy.ServiceProxy(modbusCreateServiceName, dobot_v4_bringup.srv.ModbusCreate)
    modbus_config = ModbusCreateRequest()
    modbus_config.ip = "127.0.0.1"  #IP of the gripper
    modbus_config.port = 60000  #Gripper Connection Port
    modbus_config.slave_id = 9  #Glipper Port Slave ID
    modbus_config.isRTU = 1  #RTU
    modbus_create_service(modbus_config)

    #Activate Gripper step 1: Set the registers from address 03E8 to {0,0,0}
    gripper_modbus_service = rospy.ServiceProxy(setHoldRegServiceName, dobot_v4_bringup.srv.SetHoldRegs)
    gripper_modbus_data = SetHoldRegsRequest()
    gripper_modbus_data.index = 0
    gripper_modbus_data.addr = 1000
    gripper_modbus_data.count = 3
    gripper_modbus_data.valTab = "{0,0,0}"
    gripper_modbus_data.valType = "U16"
    gripper_modbus_service(gripper_modbus_data)

    #Activate Gripper step 2: Set the registers from address 03E8 to {2034,0,0}
    gripper_modbus_data = SetHoldRegsRequest()
    gripper_modbus_data.index = 0
    gripper_modbus_data.addr = 1000
    gripper_modbus_data.count = 3
    gripper_modbus_data.valTab = "{2034,0,0}"
    gripper_modbus_data.valType = "U16"
    gripper_modbus_service(gripper_modbus_data)

    time.sleep(2)

    EnableRobot()
    #Subscribe to Digital Gripper Data Stream from Unity
    rospy.Subscriber("extend_gripper_command", GripperControl, dataCallback, queue_size=1)
    rospy.spin()