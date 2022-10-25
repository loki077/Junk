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

from MissionPlanner.Utilities import Locationwp
log_file_path = "new_log.txt"
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


#**************************Functions**************************
logging.info('Loading interface...')

if __name__ == "__main__":
    try:
        print("Main Execution begin...")
        # while True:
        #     #check for arming
        #     if cs.armed != prevArmed:
        #         if cs.armed:
        #             MissionPlanner.MainV2.speechEngine.SpeakAsync("Aircraft Armed")
        #         else:
        #             MissionPlanner.MainV2.speechEngine.SpeakAsync("Aircraft Disarmed")
        #         prevArmed = cs.armed
        #         print 'Arm loop'
        #         print 'gps status: ' + cs.gpsstatus.ToString()	
        #         print 'gps hdop	 : ' + cs.gpshdop.ToString()	
        #         print 'gps status: ' + cs.satcount.ToString()	

        #     #check for mode change
        #     if cs.mode != prevMode:
        #         MissionPlanner.MainV2.speechEngine.SpeakAsync("Mode Changed to " + cs.mode)
        #         prevMode = cs.mode
        #         print cs.mode
        #         print 'mode loop'

        #     #check for Voltage change
        #     if int(cs.battery_voltage) != int(prevBatteryVoltage):
        #         MissionPlanner.MainV2.speechEngine.SpeakAsync("Voltage Drop Change to " + int(cs.battery_voltage).ToString())
        #         prevBatteryVoltage = cs.battery_voltage
        #         print 'Voltage loop'

        #     #Print Default value
        #     if cs.armed and time.time() - prevTime > DEFAULT_LOOP_TIME:
                MissionPlanner.MainV2.speechEngine.SpeakAsync("Airspeed is " + int(cs.airspeed).ToString() + "and Groundspeed is " + int(cs.groundspeed).ToString())
                MissionPlanner.MainV2.speechEngine.SpeakAsync("Altitude is " + int(cs.alt).ToString())
                print 'check loop'
                prevTime = time.time() 
    except:
        pass

logging.info('EXIT')