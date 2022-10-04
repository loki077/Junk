###-----------------------------------------------------------------
#   File        :   gps_scan.py
#   Description :   test script to check if all CAN GPS nodes are producing Fix2 frames at the expected rate
#   Author      :   Lokesh Ramina
#   Notes       :   --
#   Date        :   04/10/2022
#   Rev History :   V 1.0
#   COPYRIGHT NOTICE: (c) 2022 Carbonix.  All rights reserved.
#   link            https://dronecan.github.io/Implementations/Pydronecan/Tutorials/2._Basic_usage/
###-----------------------------------------------------------------


'''****************************Library Import****************************'''
from logging import exception
import dronecan, time
from dronecan import uavcan
import sys
# get command line arguments
from argparse import ArgumentParser

'''****************************Constant****************************'''
REQUEST_PRIORITY = 30

DRONE_INT   = 0
DRONE_REAL  = 1
DRONE_BOOL  = 2
DRONE_STR   = 3

'''****************************Variable init****************************'''
hdop = 0
sat_cnt = 0
lat = 0
long = 0
loop_delay = 0
arm_status = False
nodeid = -1
count = 0

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

'''****************************Functions****************************'''

def handle_gps(msg):
    global hdop , sat_cnt, lat, long, loop_delay, arm_status, nodeid
    new_print = False
    payload = msg.transfer.payload

    if "uavcan.equipment.gnss.Auxiliary" in str(payload):
        nodeid = msg.transfer.source_node_id
        hdop = msg.transfer.payload.hdop
        if msg.transfer.payload.hdop > args.max_hdop: 
            print(f"{bcolors.WARNING}High HDOP Val :", msg.transfer.payload.hdop)
            new_print = True

    if "uavcan.equipment.gnss.Fix2" in str(payload):
        sat_cnt  = msg.transfer.payload.sats_used
        lat = msg.transfer.payload.latitude_deg_1e8
        long = msg.transfer.payload.longitude_deg_1e8
        if msg.transfer.payload.sats_used < args.min_sat: 
            print(f"{bcolors.WARNING}Low Sat Count : ", msg.transfer.payload.sats_used)
            new_print = True
        if msg.transfer.payload.latitude_deg_1e8 == 0: 
            print(f"{bcolors.WARNING}No Lat : ", msg.transfer.payload.latitude_deg_1e8)
            new_print = True
        if msg.transfer.payload.longitude_deg_1e8 == 0: 
            print(f"{bcolors.WARNING}Low Sat Count : ", msg.transfer.payload.longitude_deg_1e8 )
            new_print = True
        nodeid = msg.transfer.source_node_id
        tstamp = msg.transfer.ts_real
        if not nodeid in last_fix2:
            last_fix2[nodeid] = tstamp
            return
        dt = tstamp - last_fix2[nodeid]
        last_fix2[nodeid] = tstamp
        loop_delay = dt
        if dt > args.max_gap:
            print(f"{bcolors.FAIL}Loop delay =%.3f" % (dt * 1000))
            new_print = True
        # else:
            # print(f"{bcolors.HEADER}.", end = "", flush=True)

    if "ardupilot.gnss.Status" in str(payload):
        nodeid = msg.transfer.source_node_id
        if "False" in str(payload):
            arm_status = False
            print(f"{bcolors.FAIL}Node health False")
            new_print = True
        else:
            arm_status = True

   
    if new_print : 
        print(f"{bcolors.HEADER}Arm : %s LoopT : %.3fms HDOP : %.3f Sat : %u lat : %.3f long : %.3f" % (arm_status, loop_delay*1000, hdop, sat_cnt, lat, long))
    else:
        print(f"{bcolors.HEADER}Arm : %s LoopT : %.3fms HDOP : %.3f Sat : %u lat : %.3f long : %.3f" % (arm_status, loop_delay*1000, hdop, sat_cnt, lat, long) , end = '\r')

def on_send_response(e):
        if e is None:
            print('Request timed out')
        else:
            print('Param get/set response:\n %s', dronecan.to_yaml(e.response))

def send_request(name = None , value = None, value_type = DRONE_INT):
    if name is None:
        return False
    if value is None:
        return False

    try:
        if value_type == DRONE_INT:
            value = int(value)
            value = uavcan.protocol.param.Value(integer_value=value)
        elif value_type == DRONE_REAL:
            value = float(value)
            value = uavcan.protocol.param.Value(real_value=value)
        elif value_type == DRONE_BOOL:
            value = bool(value)
            value = uavcan.protocol.param.Value(boolean_value=value)
        elif value_type == DRONE_STR:
            value = str(value)
            value = uavcan.protocol.param.Value(string_value=value)
        else:
            print('wrong value type')
            return False

    except Exception as ex:
        print('Format error', 'Could not parse value', ex)
        return False

    #send cmd
    try:
        request = dronecan.uavcan.protocol.param.GetSet.Request(name= name,value=value)
        node.request(request, nodeid, on_send_response, priority=REQUEST_PRIORITY)
    except Exception as ex:
        print('Node error', 'Could not send param set request', ex)
        return False
    else:
        print('Set request sent')
        return False
    return True

'''****************************Sys Init****************************'''
parser = ArgumentParser(description='Fix2 gap example')
parser.add_argument("--bitrate", default=1000000, type=int, help="CAN bit rate")
parser.add_argument("--node-id", default=100, type=int, help="CAN node ID")
parser.add_argument("--max-gap", default=0.25, type=int, help="max gap in seconds")
parser.add_argument("--min-sat", default=10, type=int, help="min sat count")
parser.add_argument("--max-hdop", default=2.25, type=float, help="max hdop value")
parser.add_argument("port", default=None, type=str, help="serial port or mavcan URI")
args = parser.parse_args()

print("***************Arguments Configuration *************** \nLoop Delay Gap : " + str(args.max_gap * 1000) + "ms Minimum sat : " + str(args.min_sat) + " Max HDOP : " + str(args.max_hdop) + "\n******************************")

print("scan start")
try:
    # Initializing a DroneCAN node instance.
    node = dronecan.make_node(args.port, node_id=args.node_id, bitrate=args.bitrate)
    print("Node Init Successful")
except Exception as e:
    print(e)
    sys.exit()

# Initializing a node monitor
node_monitor = dronecan.app.node_monitor.NodeMonitor(node)

# callback for printing gps status 
handler = node.add_handler(dronecan.uavcan.equipment.gnss.Auxiliary, handle_gps)
handler = node.add_handler(dronecan.uavcan.equipment.gnss.Fix2, handle_gps)
handler = node.add_handler(dronecan.ardupilot.gnss.Status, handle_gps)



send_request(name= 'BRD_SERIAL_NUM' ,value= 4321)
send_request(name= 'DEBUG'          ,value= 0)
send_request(name= 'OUT1_FUNCTION'  ,value= 34)
send_request(name= 'OUT1_MIN'       ,value= 1000)
send_request(name= 'OUT1_MAX'       ,value= 1000)
    # request = dronecan.uavcan.protocol.param.GetSet.Request(name= 'OUT1_FUNCTION')
    # node.request(request, nodeid, on_send_response, priority=REQUEST_PRIORITY)

    # request = dronecan.uavcan.protocol.param.GetSet.Request(name= 'DEBUG',value=uavcan.protocol.param.Value(integer_value=1))
    # node.request(request, nodeid, on_send_response, priority=REQUEST_PRIORITY)

    # request = dronecan.uavcan.protocol.param.GetSet.Request(name= 'BRD_SERIAL_NUM',value=uavcan.protocol.param.Value(integer_value=1234))
    # node.request(request, nodeid, on_send_response, priority=REQUEST_PRIORITY)

    # request = dronecan.uavcan.protocol.param.GetSet.Request(name= 'OUT1_FUNCTION',value=uavcan.protocol.param.Value(integer_value=33))
    # node.request(request, nodeid, on_send_response, priority=REQUEST_PRIORITY)

    # request = dronecan.uavcan.protocol.param.GetSet.Request(name= 'OUT1_MIN',value=uavcan.protocol.param.Value(integer_value=0))
    # node.request(request, nodeid, on_send_response, priority=REQUEST_PRIORITY)

    # request = dronecan.uavcan.protocol.param.GetSet.Request(name= 'OUT1_MAX',value=uavcan.protocol.param.Value(integer_value=20000))
    # node.request(request, nodeid, on_send_response, priority=REQUEST_PRIORITY)


while True:
    try:
        node.spin()
    except Exception as ex:
        count = count + 1 #print(ex)
        handler.remove()
        sys.exit()

