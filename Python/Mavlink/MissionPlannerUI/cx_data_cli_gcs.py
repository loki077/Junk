###-----------------------------------------------------------------
#   File        :   cc_udp_pkt.py
#   Description :   Server To fetch radio and sat data and push it over UDP to Mission planner
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

def cli_read_udp():
    global UDPClientSocket
    msg_from_srv = UDPClientSocket.recvfrom(bufferSize)
    print("Client data read : " , msg_from_srv[0])
    return True


def cli_write_udp():
    global UDPClientSocket
    t = time.time()
    t_ms = int(t * 1000)
    message =  bytes(str(t_ms),'UTF-8')
    UDPClientSocket.sendto(message, (upd_server_ip, upd_server_port))
    print("Client data write : " ,message.decode())
    return True

'''****************************Sys Init****************************'''
log_file_path = "client.txt"
print(log_file_path)

logging.basicConfig(filename=log_file_path, level=logging.DEBUG) #format="%(asctime)s %(message)s"
'''logging.debug(message). Logs a message on a DEBUG level.
	logging.info(message). Logs a message on an INFO level.
	logging.warning(message). Logs a message on an WARNING level.
	logging.error(message). Logs a message on a ERROR level.
	logging.critical(message). Logs a message on a CRITICAL level.'''


# Create a datagram socket

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
 # Bind to address and ip

# UDPClientSocket.bind((upd_server_ip, upd_server_port))

print("UDP Client up and listening")

data_link = CxLink()

'''****************************Main****************************'''
#first write
cli_write_udp()

while True:
    # try:
    if cli_read_udp():
        cli_write_udp()

    # except Exception as ex:
    #     print(ex)
    #     sys.exit()