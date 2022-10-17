###-----------------------------------------------------------------
#   File        :   mp_udp_sat_display.py
#   Description :   To display UdP data over Missin planner coming from aircraft regarding satcom and radio
#   Author      :   Lokesh Ramina
#   Notes       :   --
#   Date        :   06/10/2022
#   Rev History :   V 1.0
#   COPYRIGHT NOTICE: (c) 2022 Carbonix.  All rights reserved.
#   link            : 
###-----------------------------------------------------------------


'''****************************Library Import****************************'''
import socket
import sys
import os
import time
from argparse import ArgumentParser
import re

'''****************************Constant****************************'''

'''****************************Variable init****************************'''
upd_server_ip   = "0.0.0.0"
upd_server_port = 10561
bufferSize = 1024
bytesToSend = str.encode("Hello")
'''****************************Class init****************************'''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class CxDataType:
    RSSI    = '000'
    NOISE   = '001'

class CxLink:
    # Pkt type
    # Start char    | Len  | Type  | Value      | End char
    #      ~:        | 000   |  000  | Data       |   :~
    #       2       |  3   |   3   | max 254    |   2
    def __init__(self):
        self.START_STR = "~:"
        self.END_STR = ":~"

    def create_pkt(self, data_type, value):
        return self.START_STR+f'{len(data_type + value):03d}'+ data_type + value + self.END_STR
    
    def extract_pkt(self, msg):
        if self.START_STR in msg:
            msg = msg.split(self.START_STR)
            if self.END_STR in msg[1]:
                msg = msg[1].split(self.END_STR)
                if int(msg[0][:3]) == len(msg[0][3:]):
                    return {'data_type':msg[0][3:6], 'value':msg[0][6:]}

'''****************************Functions****************************'''

'''****************************Sys Init****************************'''
serverAddressPort   = (upd_server_ip, upd_server_port)

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

print("UDP server connection successful")

dataLink = CxLink()
dataPkt = CxDataType()

val = dataLink.create_pkt(dataPkt.RSSI, "Yippe!!")
print(val)
print(dataLink.extract_pkt(val))
'''****************************Main****************************'''

while True:
    try:
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        time.sleep(1)
    except Exception as ex:
        print(ex)
        sys.exit()
