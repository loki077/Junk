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

from pymavlink import mavutil
from pymavlink import mavextra
import math, sys, multiprocessing, random, time, datetime, os, re
import socket
import logging
from argparse import ArgumentParser
parser = ArgumentParser(description=__doc__)

'''****************************Constant****************************'''

'''****************************Variable init****************************'''

parser.add_argument("infile", default=None, nargs='+', help="input file")
parser.add_argument("--parallel", default=4, type=int)
parser.add_argument("--threshold", type=float, default=3.0)
args = parser.parse_args()