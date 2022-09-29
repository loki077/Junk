###-----------------------------------------------------------------
#   File        :   fetch_sat_log.py
#   Description :   This script will run a loop and fetch all the satcom parameters to save and forward over mvalink if needed.
#   Author      :   Lokesh Ramina
#   Notes       :   --
#   Date        :   26/09/2022
#   Rev History :   V 1.0
#   COPYRIGHT NOTICE: (c) 2022 Carbonix.  All rights reserved.
###-----------------------------------------------------------------


'''****************************Library Import****************************'''
from __future__ import print_function
from pymavlink import mavutil #https://www.samba.org/tridge/UAV/pymavlink/apidocs/nameIndex.html
import requests
import sys
import math
import time
import datetime
import logging
from argparse import ArgumentParser

'''****************************Sys Init****************************'''
print("fetch_sat_log.py init")

parser = ArgumentParser(description='This script will run a loop and fetch all the satcom parameters to save and forward over mvalink if needed.')
parser.add_argument('--connect', 
                   help="vehicle connection target string")
parser.add_argument('--restapi', 
                   help="vehicle connection target string")

args = parser.parse_args()

mavlink_connect_str=args.connect
rest_api_str=args.restapi

#Stop code if not parse
if not args.connect and not args.restapi:
    print("Error : Please pass a argument to connet example: --connect udp:127.0.0.1:14550 --restapi https://w3schools.com/python/demopage.htm")
    sys.exit()
if not mavlink_connect_str and not rest_api_str:
    print("Error : Please pass a correct argument to connet example: --connect udpout:127.0.0.1:14550 --restapi https://w3schools.com/python/demopage.htm")
    sys.exit()


'''****************************Functions****************************'''

def wait_conn():
    """
    Sends a ping to stabilish the UDP communication and awaits for a response
    """
    msg = None
    print("Send Mav Ping " + mavlink_connect_str)
    while not msg:
        msrc.mav.ping_send(
            int(time.time() * 1e6), # Unix time in microseconds
            0, # Ping number
            0, # Request ping of all systems
            0 # Request ping of all components
        )
        msg = msrc.recv_match()
        time.sleep(0.5)

def print_mav_net_status():
    print("%u sent, %u received, %u errors " % (
    msrc.mav.total_packets_sent,
    msrc.mav.total_packets_received,
    msrc.mav.total_receive_errors))

def radio_status_send():
    ''' rssi	uint8_t		Local signal strength
        remrssi	uint8_t		Remote signal strength
        txbuf	uint8_t	%	Remaining free buffer space.
        noise	uint8_t		Background noise level
        remnoise	uint8_t		Remote background noise level
        rxerrors	uint16_t		Receive errors
        fixed	uint16_t		Count of error corrected packets'''
    RSSI_109        = 0
    REM_RSSI_109    = 1
    TX_BUFF_109     = 2
    NOISE_109       = 3
    REM_NOISE_109   = 4
    RX_ERRORS_109   = 5
    FIXED_109       = 6

    radio_status_value = [] 
    radio_status_value.append(122)
    radio_status_value.append(0)
    radio_status_value.append(0)
    radio_status_value.append(0)
    radio_status_value.append(0)
    radio_status_value.append(0)
    radio_status_value.append(0)

    msrc.mav.command_long_send(
        msrc.target_system,
        msrc.target_component,
        mavutil.mavlink.RADIO_STATUS,
        0, #initial cmd
        radio_status_value[RSSI_109], radio_status_value[REM_RSSI_109], radio_status_value[TX_BUFF_109], 
        radio_status_value[NOISE_109],radio_status_value[REM_NOISE_109], radio_status_value[RX_ERRORS_109],
        radio_status_value[FIXED_109] 
       )
    
'''****************************MAV Init****************************'''

print("Setting up Mavlink connection to " + mavlink_connect_str)
msrc = mavutil.mavlink_connection(mavlink_connect_str, source_system=2)

wait_conn()
print("Mavlink connection to " + mavlink_connect_str + " Successfull")

msrc.wait_heartbeat()
print("Heartbeat from APM (system %u component %u)" % (msrc.target_system, msrc.target_component))
print(msrc.target_system)

msrc.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_DEBUG,
                           "Satcom Script Init".encode())

msrc.mav.command_long_send(
        255,
        190,
        mavutil.mavlink.MAVLINK_MSG_ID_STATUSTEXT,
        0, #initial cmd
        6,'a',0,0,0,0,0
       )
'''****************************Rest API Init****************************'''

# # defining a params dict for the parameters to be sent to the API
# PARAMS = {'address':location}
  
# # sending get request and saving the response as response object
# rest_cli = requests.get(url = rest_api_str, params = PARAMS)
  
# # extracting data in json format
# data_resp = rest_cli.json()


if __name__ == "__main__":
    try:
        print("Main Execution begin...")
        print_mav_net_status()
        while True:
            m = msrc.recv_msg()
            # radio_status_send()
            if m is not None: 
                print(msrc.recv_match().to_dict())
    except:
        pass
           
    # except KeyboardInterrupt:
    #     sys.exit()


# mav2.recv_match(type='SYS_STATUS', condition='SYS_STATUS.mode==2 and SYS_STATUS.nav_mode==4', blocking=True)

# print("Setting declination")
# mav1.mav.param_set_send(mav1.target_system, mav1.target_component,
#                        'COMPASS_DEC', radians(12.33))
# mav2.mav.param_set_send(mav2.target_system, mav2.target_component,
#                        'COMPASS_DEC', radians(12.33))
