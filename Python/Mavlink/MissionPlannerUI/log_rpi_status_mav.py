print('\n*** Carbonix Mission Planner Initializing... ***\n')
print('Loading modules...')

# ************************** Import Modules**************************
import sys
import math
import clr
import time
import datetime
import logging
from collections import OrderedDict

clr.AddReference('MAVLink')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')
clr.AddReference("MissionPlanner")
clr.AddReference("MissionPlanner.Utilities") # includes the Utilities class

import MAVLink
import MissionPlanner

from System import Char, Func, Array
from System.Windows.Forms import Application, Screen, Form, Keys, HorizontalAlignment, \
    FlatStyle, BorderStyle, ProgressBar, CheckBox, Label, NumericUpDown, Button, ToolTip
from System.Drawing import Point, Color

from MissionPlanner.Utilities import Locationwp
log_file_path = "C:\\Users\\Lokesh\\Documents\\Mission Planner\\logs\\my_new_log_"+datetime.datetime.now().ToString().split(".")[0].replace(':','-')+".txt"
print(log_file_path)
logging.basicConfig(filename=log_file_path, level=logging.DEBUG) #format="%(asctime)s %(message)s"
'''logging.debug(message). Logs a message on a DEBUG level.
    logging.info(message). Logs a message on an INFO level.
    logging.warning(message). Logs a message on an WARNING level.
    logging.error(message). Logs a message on a ERROR level.
    logging.critical(message). Logs a message on a CRITICAL level.'''

#**************************Constants**************************
DEFAULT_LOOP_TIME = 5.0
SEVERITY = ['EMERGENCY: ', 'ALERT: ', 'CRITICAL: ', 'ERROR: ', 'WARNING: ', 'NOTICE: ', 'INFO: ', 'DEBUG: ']
SPINNER = ['-', '\\', '|', '/']


#**************************variables**************************
prevArmed = -1
prevMode = ""
prevBatteryVoltage = ""
prevTime = 0


#**************************Class**************************
class MPColor:
    """ System.Drawing.Color is a sealed value type that disallows class inheritance
        Dynamically creating MPColor attributes is a workaround for that """

    def __init__(self):
        pass

for attr in dir(Color):
    setattr(MPColor, attr, getattr(Color, attr))

setattr(MPColor, 'MPDarkGray', Color.FromArgb(38, 39, 40))
setattr(MPColor, 'MPMediumGray', Color.FromArgb(53, 54, 55))
setattr(MPColor, 'MPLightGray', Color.FromArgb(68, 69, 70))
setattr(MPColor, 'MPGreen', Color.FromArgb(165, 203, 70))
setattr(MPColor, 'ServoBG', Color.FromArgb(200, 201, 202))

CustomColor = MPColor() 


class CarbonixInitForm(Form):
    def __init__(self):
        MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.HEARTBEAT,
                                  Func[MAVLink.MAVLinkMessage, bool](self.heartbeat_received))
        MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.RAW_IMU,
                                  Func[MAVLink.MAVLinkMessage, bool](self.raw_imu_received))
        MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.VFR_HUD,
                                  Func[MAVLink.MAVLinkMessage, bool](self.check_airspeed_received))
        MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.RADIO_STATUS,
                                  Func[MAVLink.MAVLinkMessage, bool](self.check_radio_status))                          
        MAV.OnPacketReceived += self.packet_handler
        self.heartbeat_count = 0

                
    def check_airspeed_received(self, message):
        data = 'check_airspeed_received ' + getattr(message.data, 'airspeed').ToString()
        # print()
        # logging.debug(data)

    def heartbeat_received(self, message):
        data = 'heartbeat_received ' + message.data.ToString()
        # print(data)
        # logging.debug(data)

    def raw_imu_received(self, message):
        data = 'raw_imu_received ' + getattr(message.data, 'xacc').ToString()
        # print(data)
        # logging.debug(data)
    
    def check_radio_status(self, message):
        data = 'check_radio_status ' + message.data.ToString()
        print(data)
        logging.debug(data)

    def packet_handler(self, obj, message):
        try:
            data = "Data : ID:" + str(MAVLink.MAVLINK_MSG_ID) + " msg:" + str(message)
            if "RADIO_STATUS" in str(message):
                logging.debug( "::" + str(message))
            if message.msgid == MAVLink.MAVLINK_MSG_ID.STATUSTEXT.value__:
                print(SPINNER[self.heartbeat_count] + ' ' + SEVERITY[message.data.severity] + str(bytes(message.data.text)))
        except Exception as inst:
            print(inst)  # not sure what situation would raise this, so leaving it for debugging

    def on_exit(self, sender, event):
        print('on_exit')
        MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.HEARTBEAT)        
        MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.VFR_HUD)
        MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.RAW_IMU)
        MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.RADIO_STATUS)


#**************************Functions**************************
logging.info('Loading interface...')
Application.Run(CarbonixInitForm())
logging.info('EXIT')