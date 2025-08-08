#!/usr/bin/env python3

import rospy

def initialize_global():
    print("Global Variables initialized")

    global gripper_prev_state,gripper_initialization,gripper_data_count

    gripper_prev_state = 0
    gripper_initialization = False
    gripper_data_count = 0
