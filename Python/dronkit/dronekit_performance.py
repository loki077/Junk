#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
from __future__ import print_function
from dronekit import connect
from pymavlink import mavutil
import time
import sys
from datetime import datetime


#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Generates RC channel tracking to see any drop in data')
parser.add_argument('--connect', 
                   help="vehicle connection target string")
args = parser.parse_args()

connection_string=args.connect

#Stop code if not parse
if not args.connect:
    print("Error : Please pass a argument to connet example: --connect udp:127.0.0.1:14550")
    sys.exit()
if not connection_string:
    print("Error : Please pass a correct argument to connet example: --connect udp:127.0.0.1:14550")
    sys.exit()

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

#global vehicle


def cur_usec():
    """Return current time in usecs"""
    # t = time.time()
    dt = datetime.now()
    t = dt.minute * 60 + dt.second + dt.microsecond / (1e6)
    return t

class MeasureTime(object):
    def __init__(self):
        self.prevtime = cur_usec()
        self.previnterval = 0
        self.numcount = 0
        self.reset()

    def reset(self):
        self.maxinterval = 0
        self.mininterval = 10000
        
    def log(self):
        #print "Interval", self.previnterval
        #print "MaxInterval", self.maxinterval
        #print "MinInterval", self.mininterval
        sys.stdout.write('MaxInterval: %s\tMinInterval: %s\tInterval: %s\r' % (self.maxinterval,self.mininterval, self.previnterval) )
        sys.stdout.flush()


    def update(self):
        now = cur_usec()
        self.numcount = self.numcount + 1
        self.previnterval = now - self.prevtime
        self.prevtime = now
        if self.numcount>1: #ignore first value where self.prevtime not reliable.
            self.maxinterval = max(self.previnterval, self.maxinterval)
            self.mininterval = min(self.mininterval, self.previnterval)
            self.log()


#object to calculate measure time
acktime = MeasureTime()


#Create COMMAND_ACK message listener.
@vehicle.on_message('COMMAND_ACK')
def listener(self, name, message):
    acktime.update()
    send_testpackets()


def send_testpackets():
    #Send message using `command_long_encode` (returns an ACK)
    msg = vehicle.message_factory.command_long_encode(
                                                    1, 1,    # target system, target component
                                                    #mavutil.mavlink.MAV_CMD_DO_SET_RELAY, #command
                                                    mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
                                                    0, #confirmation
                                                    0, 0, 0, 0, #params 1-4
                                                    0,
                                                    0,
                                                    0
                                                    )

    vehicle.send_mavlink(msg)

#Start logging by sending a test packet
send_testpackets()

print("Logging for 30 seconds")
for x in range(1,30):
    time.sleep(1)

# Close vehicle object before exiting script
vehicle.close()


