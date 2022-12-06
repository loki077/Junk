#Need to add the below code in AP_gps_.cpp
#GCS_SEND_TEXT(MAV_SEVERITY_CRITICAL, "GPS_LOG,%u,%u,%u,%u,%f  ",t.last_fix_time_ms,t.last_message_time_ms,t.delta_time_ms,t.delayed_count,t.average_delta_ms);
###-----------------------------------------------------------------
#   File        :   gps_scan.py
#   Description :   test script to check if all CAN GPS nodes are producing Fix2 frames at the expected rate
#   Author      :   Lokesh Ramina
#   Notes       :   --
#   Date        :   04/10/2022
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
from dronecan import uavcan
import sys
# get command line arguments
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMessageBox, QComboBox, QToolBar 
import serial.tools.list_ports
import glob

'''****************************Function****************************'''

def print_gps_data(msg):
    payload = msg.transfer.payload
    # if "uavcan.equipment.gnss.Auxiliary" in str(payload):
    # if "uavcan.equipment.gnss.Fix2" in str(payload):
    if "ardupilot.gnss.Status" in str(payload):
        print(payload)
    if "uavcan.protocol.debug.LogMessage" in str(payload):
        if "GPS_LOG" in payload:
            print(payload)

'''****************************Sys Init****************************'''


parser = ArgumentParser(description='Fix2 gap example')
parser.add_argument("--bitrate", default=1000000, type=int, help="CAN bit rate")
parser.add_argument("--node-id", default=11, type=int, help="CAN node ID")
parser.add_argument("port", default=None, type=str, help="serial port or mavcan URI")
args = parser.parse_args()

print("***************Arguments Configuration *************** \nLoop Delay Gap : " + str(args.max_gap * 1000) + "ms Minimum sat : " + str(args.min_sat) + " Max HDOP : " + str(args.max_hdop) + "\n******************************")


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

callback for printing gps status 
handler = node.add_handler(dronecan.uavcan.equipment.gnss.Auxiliary, print_gps_data)
handler = node.add_handler(dronecan.uavcan.equipment.gnss.Fix2, print_gps_data)
handler = node.add_handler(dronecan.ardupilot.gnss.Status, print_gps_data)
handler = node.add_handler(dronecan.uavcan.protocol.debug.LogMessage, print_gps_data)

while True:
    try:
        node.spin()
    except Exception as ex:
        handler.remove()