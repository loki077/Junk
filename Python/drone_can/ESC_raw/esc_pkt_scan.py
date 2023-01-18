#Need to add the below code in AP_gps_.cpp
#GCS_SEND_TEXT(MAV_SEVERITY_CRITICAL, "GPS_LOG,%u,%u,%u,%u,%f  ",t.last_fix_time_ms,t.last_message_time_ms,t.delta_time_ms,t.delayed_count,t.average_delta_ms);
###-----------------------------------------------------------------
#   File        :   esc_pkt_scan.py
#   Description :   test script to check if all CAN GPS nodes are producing Fix2 frames at the expected rate
#   Author      :   Lokesh Ramina
#   Notes       :   --
#   Date        :   12/12/2022
#   Rev History :   V 1.0
#   COPYRIGHT NOTICE: (c) 2022 Carbonix.  All rights reserved.
#   link            https://dronecan.github.io/Implementations/Pydronecan/Tutorials/2._Basic_usage/
#                   https://www.guru99.com/pyqt-tutorial.html
#                   https://realpython.com/python-pyqt-layout/
###-----------------------------------------------------------------


'''****************************Library Import****************************'''
from logging import exception
# from msilib.schema import SelfReg
import time
import dronecan
import sys
# get command line arguments
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMessageBox, QComboBox, QToolBar 
import serial.tools.list_ports
import glob
import random
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time 
import threading
import multiprocessing

# Create figure for plotting
fig, ax = plt.subplots()
ax2 = ax.twinx()



esc_0 = [0]
esc_1 = [0]
esc_0_rpm = [0]
esc_1_rpm = [0]

max_size = -1000
random.seed(5)

'''****************************Function****************************'''
# This function is called periodically from FuncAnimation
def animate(i):
    global esc_0, esc_1, esc_0_rpm, esc_1_rpm

    # Limit x and y lists to 20 items
    esc_0 = esc_0[max_size:]
    esc_1 = esc_1[max_size:]
    esc_0_rpm = esc_0_rpm[max_size:]
    esc_1_rpm = esc_1_rpm[max_size:]

    try: 
        # Draw x and y lists
        ax.clear()
        ax2.clear()
        ax.set_ylim([0, 2000])
        ax2.set_ylim([0, 8000])

        plt1 = ax.plot(esc_0, label = "esc_0", linestyle="-")
        plt2 = ax.plot(esc_1, label = "esc_1", linestyle="-")

        plt3 = ax2.plot(esc_0_rpm, label = "esc_0_rpm", linestyle="--")
        plt4 = ax2.plot(esc_1_rpm, label = "esc_0_rpm", linestyle="--")

        # added these three lines
        lns = plt1+plt2+plt3+plt4
        labs = [l.get_label() for l in lns]
        # ax.legend(lns, labs, loc=0)
        # Format plot
        # plt.xticks(rotation=45, ha='right')
        # plt.subplots_adjust(bottom=0.30)
        # plt.title('ESC Raw Value')
        fig.legend(loc="upper right")
    except Exception as e:
            print(e)


def print_esc_data(msg):
    global esc_0, esc_1, esc_0_rpm, esc_1_rpm
    #sample : uavcan.equipment.esc.RawCommand(cmd=ArrayValue(type=saturated int14[<=20], items=[0, 0]))
    payload = msg.transfer.payload
    if("cmd" in str(payload)):
        try:
            # print("esc_0:" + str(msg.transfer.payload.cmd[0]))
            # print("esc_1:" + str(msg.transfer.payload.cmd[1]))
            esc_0.append(msg.transfer.payload.cmd[0])
            esc_1.append(msg.transfer.payload.cmd[1])
            esc_0_rpm.append(esc_0_rpm[-1])
            esc_1_rpm.append(esc_1_rpm[-1])
        except Exception as e:
            print(e)
   

def print_node_status(msg):
    global esc_0, esc_1, esc_0_rpm, esc_1_rpm
    payload = msg.transfer.payload
    esc_0.append(random.random())
    esc_1.append(random.random())
    esc_0_rpm.append(random.random())
    esc_1_rpm.append(random.random())
    
def print_esc_status(msg):
    global esc_0, esc_1, esc_0_rpm, esc_1_rpm
    payload = msg.transfer.payload
    try:
        if(msg.transfer.payload.esc_index == 0):
            # print("esc_0_rpm:" + str(msg.transfer.payload.rpm))
            esc_0_rpm.append(msg.transfer.payload.rpm)
            esc_0.append(esc_0[-1])
            esc_1.append(esc_1[-1])
            esc_1_rpm.append(esc_1_rpm[-1])
        if(msg.transfer.payload.esc_index == 1):
            # print("esc_1_rpm:" + str(msg.transfer.payload.rpm))
            esc_1_rpm.append(msg.transfer.payload.rpm)
            esc_0.append(esc_0[-1])
            esc_1.append(esc_1[-1])
            esc_0_rpm.append(esc_0_rpm[-1])
    except Exception as e:
        print(e)
  
'''****************************Sys Init****************************'''

parser = ArgumentParser(description='Fix2 gap example')
parser.add_argument("--bitrate", default=1000000, type=int, help="CAN bit rate")
parser.add_argument("--node-id", default=11, type=int, help="CAN node ID")
parser.add_argument("port", default=None, type=str, help="serial port or mavcan URI")
args = parser.parse_args()

try:
    # Initializing a DroneCAN node instance.
    node = dronecan.make_node(str(args.port), node_id=int(args.node_id), bitrate=args.bitrate)
    node_id = int(args.node_id)
    # Initializing a node monitor
    node_monitor = dronecan.app.node_monitor.NodeMonitor(node)
    print("CAN Node Init Successful")
except Exception as e:
    print(e)
    sys.exit()

#create handler
handler = node.add_handler(dronecan.uavcan.equipment.esc.RawCommand, print_esc_data)
# handler = node.add_handler(dronecan.uavcan.protocol.NodeStatus, print_node_status)
handler = node.add_handler(dronecan.uavcan.equipment.esc.Status, print_esc_status)

#init thread
# p1 = multiprocessing.Process(target=node.spin)
node_thread = threading.Thread(target=node.spin)

# start thread
node_thread.start()
# p1.start()

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

handler.remove()