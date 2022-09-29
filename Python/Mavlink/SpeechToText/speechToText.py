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
log_file_path = "C:\\Users\\Lokesh\\Dropbox (Carbonix Company)\\PC\\Documents\\Mission Planner\\logs\\my_log_"+datetime.datetime.now().ToString().split(".")[0].replace(':','-')+".txt"
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
		MAV.OnPacketReceived += self.packet_handler
		
		#Header
		self.Header 	= 'Carbonix Mission Planner'
		self.Location 	= Point(0, 0)
		self.TopMost 	= True
		self.BackColor 	= CustomColor.MPDarkGray
		self.ForeColor 	= CustomColor.White
		self.Shown 		+= self.on_load
		self.FormClosing += self.on_exit
		self.heartbeat_count = 0
		self.margin = 5
		start_x, start_y = 12, 10


		self.mp_widgets = []

		progress_bar = ProgressBar()
		progress_bar.Width = 150
		progress_bar.Height = 20
		progress_bar.BackColor = CustomColor.MPMediumGray
		progress_bar.ForeColor = CustomColor.MPGreen
		progress_bar.Minimum = 0
		progress_bar.Maximum = 100
		progress_bar.Value = 10
		progress_bar.Text = "Initializing"

		lbl_loading = Label()
		lbl_loading.Text = 'Label'
		lbl_loading.BackColor = CustomColor.MPDarkGray
		lbl_loading.Width = 60
		lbl_loading.Height = progress_bar.Height - 8

		self.mp_widgets.append(OrderedDict([('lbl_loading', lbl_loading),
											   ('progress_bar', progress_bar)
											   ]))
	def set_sticky(self, sender, event):
		print('set_sticky')
		if sender.Checked:
			self.TopMost = True
			return
		self.TopMost = False
		
	def check_airspeed_received(self, message):
		print('check_airspeed_received ' + getattr(message.data, 'airspeed').ToString())

	def heartbeat_received(self, message):
		print('heartbeat_received')

	def raw_imu_received(self, message):
		print('raw_imu_received ' + getattr(message.data, 'xacc').ToString())

	def handle_overrides(self, sender, event):
		print('handle_overrides')
		if sender == self.btn_inhibit_overrides:
			if self.chk_aileron.Checked:
				self.chk_aileron.Checked = False
			if self.chk_elevator.Checked:
				self.chk_elevator.Checked = False
			if self.chk_throttle.Checked:
				self.chk_throttle.Checked = False
			if self.chk_rudder.Checked:
				self.chk_rudder.Checked = False
			if self.chk_channel.Checked:
				self.chk_channel.Checked = False
			return

		chan, name = sender.Name.split(',')
		chan = int(chan)

		if sender.Checked:
			val = int(getattr(self, name).Value)
			Script.SendRC(chan, val, True)
			if sender.BackColor != Color.DarkRed:
				sender.BackColor = Color.DarkRed
			return

		if event is not None:  # return RC control for this channel by sending a 0 pwm value
			""" https://diydrones.com/forum/topics/how-to-restore-control-back-to-rc-when-running-a-python-script-in """
			Script.SendRC(chan, 0, True)
			if sender.BackColor != self.BackColor:
				sender.BackColor = self.BackColor

	def packet_handler(self, obj, message):
		try:
			data = "Data : ID:" + str(MAVLink.MAVLINK_MSG_ID) + " msg:" + str(message)
			logging.debug(data)
			if message.msgid == MAVLink.MAVLINK_MSG_ID.STATUSTEXT.value__:
				print(SPINNER[self.heartbeat_count] + ' ' + SEVERITY[message.data.severity] + str(bytes(message.data.text)))
		except Exception as inst:
			print(inst)  # not sure what situation would raise this, so leaving it for debugging

	def on_load(self, sender, event):
		print('on_load')
		# self.chk_sticky.CheckedChanged += self.set_sticky
		# self.set_sticky(self.chk_sticky, None)
		print('Running...')

	def on_exit(self, sender, event):
		print('on_exit')
		MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.SERVO_OUTPUT_RAW)
		MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.HEARTBEAT)

#**************************Functions**************************
logging.info('Loading interface...')
Application.Run(CarbonixInitForm())
logging.info('EXIT')

# #**************************Configuration**************************
# MissionPlanner.MainV2.speechEnable = True



# #**************************Start up**************************
# print 'CX - Start Python Script'
# MissionPlanner.MainV2.speechEngine.SpeakAsync("Welcome to Carbonix Mission Planner")
# MissionPlanner.MainV2.speechEngine.SpeakAsync("Please wait for an Auto Check")
# Script.Sleep(10000)


# # GPS check on start
# while cs.lat == 0:
# 	MissionPlanner.MainV2.speechEngine.SpeakAsync("Waiting for GPS")
# 	print 'Waiting for GPS'
# 	Script.Sleep(10000)

# while cs.satcount < 10:
# 	MissionPlanner.MainV2.speechEngine.SpeakAsync("Sattelite count is Low ")
# 	print 'Sat Count low'
# 	Script.Sleep(10000)

# while cs.gpshdop > 2:
# 	MissionPlanner.MainV2.speechEngine.SpeakAsync("HDOP value is low ")
# 	print 'HDOP value high'
# 	Script.Sleep(10000)

# MissionPlanner.MainV2.speechEngine.SpeakAsync("GPS working, sat count is " + cs.satcount.ToString() + " hdop value is " + cs.gpshdop.ToString())
# print 'GPS working, sat count : ' + cs.satcount.ToString() +', hdop : ' + cs.gpshdop.ToString()


# cs.messages.Clear()

# while True:
# 	#check for arming
# 	if cs.armed != prevArmed:
# 		if cs.armed:
# 			MissionPlanner.MainV2.speechEngine.SpeakAsync("Aircraft Armed")
# 		else:
# 			MissionPlanner.MainV2.speechEngine.SpeakAsync("Aircraft Disarmed")
# 		prevArmed = cs.armed
# 		print 'Arm loop'
# 		print 'gps status: ' + cs.gpsstatus.ToString()	
# 		print 'gps hdop	 : ' + cs.gpshdop.ToString()	
# 		print 'gps status: ' + cs.satcount.ToString()	

# 	#check for mode change
# 	if cs.mode != prevMode:
# 		MissionPlanner.MainV2.speechEngine.SpeakAsync("Mode Changed to " + cs.mode)
# 		prevMode = cs.mode
# 		print cs.mode
# 		print 'mode loop'

# 	# #check for Voltage change
# 	# if int(cs.battery_voltage) != int(prevBatteryVoltage):
# 	# 	MissionPlanner.MainV2.speechEngine.SpeakAsync("Voltage Drop Change to " + int(cs.battery_voltage).ToString())
# 	# 	prevBatteryVoltage = cs.battery_voltage
# 	# 	print 'Voltage loop'

# 	#Print Default value
# 	if cs.armed and time.time() - prevTime > DEFAULT_LOOP_TIME:
# 		MissionPlanner.MainV2.speechEngine.SpeakAsync("Airspeed is " + int(cs.airspeed).ToString() + "and Groundspeed is " + int(cs.groundspeed).ToString())
# 		MissionPlanner.MainV2.speechEngine.SpeakAsync("Altitude is " + int(cs.alt).ToString())
# 		print 'check loop'
# 		prevTime = time.time() 
