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


'''****************************Constant****************************'''
REQUEST_PRIORITY = 30

DRONE_INT   = 0
DRONE_REAL  = 1
DRONE_BOOL  = 2
DRONE_STR   = 3

STANDARD_BAUD_RATES = 9600, 115200, 460800, 921600, 1000000, 3000000
DEFAULT_BAUD_RATE = 115200
assert DEFAULT_BAUD_RATE in STANDARD_BAUD_RATES

'''****************************Variable init****************************'''
hdop = 0
sat_cnt = 0
lat = 0
long = 0
loop_delay = 0
arm_status = False
node_id = -1

send_cmd = ""
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

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QVBoxLayout, QTabWidget, QCheckBox, QGroupBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QComboBox, QCompleter, QDialog, QDirModel, QFileDialog, QGroupBox, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QGridLayout, QCheckBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIntValidator

class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('GPS Test Tool carbonix.com.au')
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)              # This is required to stop background timers!
        self.width = 800
        self.height = 500
        self.resize(self.width, self.height)

        self.bitrate = QSpinBox(self)
        self.bitrate.setMaximum(1000000)
        self.bitrate.setMinimum(10000)
        self.bitrate.setValue(1000000)

        self.bus_number = QSpinBox(self)
        self.bus_number.setMaximum(4)
        self.bus_number.setMinimum(1)
        self.bus_number.setValue(1)
        
        self.baudrate = QComboBox(self)
        self.baudrate.setEditable(True)
        self.baudrate.setInsertPolicy(QComboBox.NoInsert)
        self.baudrate.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.baudrate_completer = QCompleter(self)
        self.baudrate_completer.setModel(self.baudrate.model())
        self.baudrate.setCompleter(self.baudrate_completer)

        self.baudrate.setValidator(QIntValidator(min(STANDARD_BAUD_RATES), max(STANDARD_BAUD_RATES)))
        self.baudrate.insertItems(0, map(str, STANDARD_BAUD_RATES))
        self.baudrate.setCurrentText(str(DEFAULT_BAUD_RATE))

        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(self.can_connection_wg(), "Connection")
        tabs.addTab(self.test_wg(), "Test")
        layout.addWidget(tabs)
    
    def list_serial_port(self):
        """Returns dictionary, where key is description, value is the OS assigned name of the port"""
        # Linux system
        ifaces = glob.glob('/dev/serial/by-id/*')
        try:
            ifaces = list(sorted(ifaces,
                                    key=lambda s: not ('zubax' in s.lower() and 'babel' in s.lower())))
        except Exception:
            logger.warning('Sorting failed', exc_info=True)

        for x in ifaces:
            print(x)
        return ifaces

    def can_connection_wg(self):
        """Create the can connection page UI."""
        wg_tab = QWidget()
        can_group = QGroupBox('CAN interface setup', self)

        can_layout = QVBoxLayout()
        can_layout.addWidget(QLabel('Select CAN interface'))
        available_port = QComboBox(self)
        available_port.addItems(self.list_serial_port())
        can_layout.addWidget(available_port)
        
        adapter_group = QGroupBox('Adapter settings', self)
        adapter_layout = QGridLayout()
        adapter_layout.addWidget(QLabel('Bus Number:'), 0, 0)
        adapter_layout.addWidget(self.bus_number, 0, 1)
        adapter_layout.addWidget(QLabel('CAN bus bit rate:'), 1, 0)
        adapter_layout.addWidget(self.bitrate, 1, 1)
        adapter_layout.addWidget(QLabel('Adapter baud rate (not applicable to USB):'), 2, 0)
        adapter_layout.addWidget(self.baudrate, 2, 1)
        
        adapter_group.setLayout(adapter_layout)
        can_layout.addWidget(adapter_group)
        can_group.setLayout(can_layout)

        layout = QVBoxLayout()
        layout.addWidget(can_group)
        wg_tab.setLayout(layout)

        return wg_tab

    def test_wg(self):
        """Create the Network page UI."""
        wg_tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox("Network Option 1"))
        layout.addWidget(QCheckBox("Network Option 2"))
        wg_tab.setLayout(layout)
        return wg_tab

'''****************************Functions****************************'''

def handle_gps(msg):
    global hdop , sat_cnt, lat, long, loop_delay, arm_status, node_id
    new_print = False
    payload = msg.transfer.payload

    if "uavcan.equipment.gnss.Auxiliary" in str(payload):
        node_id = msg.transfer.source_node_id
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
        node_id = msg.transfer.source_node_id
        tstamp = msg.transfer.ts_real
        if not node_id in last_fix2:
            last_fix2[node_id] = tstamp
            return
        dt = tstamp - last_fix2[node_id]
        last_fix2[node_id] = tstamp
        loop_delay = dt
        if dt > args.max_gap:
            print(f"{bcolors.FAIL}Loop delay =%.3f" % (dt * 1000))
            new_print = True
        # else:
            # print(f"{bcolors.HEADER}.", end = "", flush=True)

    if "ardupilot.gnss.Status" in str(payload):
        node_id = msg.transfer.source_node_id
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

def on_send_response(msg):
        if msg is None:
            print('Request timed out')
        else:
            print('Param get/set response: %s', dronecan.to_yaml(msg.response.value.integer_value))

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
        node.request(request, node_id, on_send_response, priority=REQUEST_PRIORITY)
        print("Send Request: ",name, " : ",  value)
    except Exception as ex:
        print('Node error', 'Could not send param set request', ex)
        return False
    else:
        return False
    return True


def connect_node(connection_port, node_id_data):
    try:
        # Initializing a DroneCAN node instance.
        node = dronecan.make_node(connection_port, node_id=node_id_data, bitrate=args.bitrate)
        node_id = node_id_data
        # Initializing a node monitor
        node_monitor = dronecan.app.node_monitor.NodeMonitor(node)
        print("CAN Node Init Successful")
    except Exception as e:
        print(e)
        sys.exit()


'''****************************Sys Init****************************'''


parser = ArgumentParser(description='Fix2 gap example')
parser.add_argument("--bitrate", default=1000000, type=int, help="CAN bit rate")
parser.add_argument("--node-id", default=100, type=int, help="CAN node ID")
parser.add_argument("--max-gap", default=0.25, type=int, help="max gap in seconds")
parser.add_argument("--min-sat", default=10, type=int, help="min sat count")
parser.add_argument("--max-hdop", default=2.25, type=float, help="max hdop value")
parser.add_argument("--port", default=None, type=str, help="serial port or mavcan URI")
args = parser.parse_args()

print("***************Arguments Configuration *************** \nLoop Delay Gap : " + str(args.max_gap * 1000) + "ms Minimum sat : " + str(args.min_sat) + " Max HDOP : " + str(args.max_hdop) + "\n******************************")


# callback for printing gps status 
# handler = node.add_handler(dronecan.uavcan.equipment.gnss.Auxiliary, handle_gps)
# handler = node.add_handler(dronecan.uavcan.equipment.gnss.Fix2, handle_gps)
# handler = node.add_handler(dronecan.ardupilot.gnss.Status, handle_gps)

#send Pre Configuration cmd
# send_request(name= 'BRD_SERIAL_NUM' ,value= 1234)
# send_request(name= 'DEBUG'          ,value= 0)
# send_request(name= 'OUT1_FUNCTION'  ,value= 34)
# send_request(name= 'OUT1_MIN'       ,value= 1000)
# send_request(name= 'OUT1_MAX'       ,value= 1000)

'''****************************Main Loop****************************'''




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
    # while True:
    #     try:
    #         node.spin()
    #     except Exception as ex:
    #         handler.remove()



