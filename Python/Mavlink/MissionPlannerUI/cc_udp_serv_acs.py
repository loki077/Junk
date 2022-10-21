###-----------------------------------------------------------------
#   File        :   cc_udp_sat_log.py
#   Description :   CLient: To fetch radio and sat data and push it over UDP to Mission planner
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
import logging
import datetime

'''****************************Constant****************************'''

'''****************************Variable init****************************'''
upd_server_ip   = "0.0.0.0"
upd_server_port = 10561

bufferSize = 1024

cli_address = ""
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

RSSI    = '000'
NOISE   = '001'
TIME_STAMP   = '002'

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

def srv_read_udp():
    global UDPServerSocket, cli_address
    msg_from_srv = UDPServerSocket.recvfrom(bufferSize)
    message = msg_from_srv[0]
    cli_address = msg_from_srv[1]
    print("Server data read : " , message)
    return True


def srv_write_udp():
    global UDPServerSocket
    t = time.time()
    t_ms = int(t * 1000)
    # message = data_link.create_pkt(str(t_ms),TIME_STAMP)
    UDPServerSocket.sendto(str(t_ms).encode(encoding = 'UTF-8'), (upd_server_ip, cli_address))
    print("Server data write : " ,str(t_ms))
    return True

'''****************************Sys Init****************************'''
log_file_path = "server.txt"
print(log_file_path)

logging.basicConfig(filename=log_file_path, level=logging.DEBUG) #format="%(asctime)s %(message)s"
'''logging.debug(message). Logs a message on a DEBUG level.
	logging.info(message). Logs a message on an INFO level.
	logging.warning(message). Logs a message on an WARNING level.
	logging.error(message). Logs a message on a ERROR level.
	logging.critical(message). Logs a message on a CRITICAL level.'''


# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 # Bind to address and ip

UDPServerSocket.bind((upd_server_ip, upd_server_port))

print("UDP server up and listening")

data_link = CxLink()

'''****************************Main****************************'''

while True:
    # try:
    if srv_read_udp():
        srv_write_udp()
        time.sleep(1)
    # except Exception as ex:
    #     print(ex)
    #     sys.exit()