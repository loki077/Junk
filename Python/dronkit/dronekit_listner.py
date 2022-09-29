#examples Links below:
#https://www.programcreek.com/python/example/107366/dronekit.connect


from dronekit import connect
import time
import sys
from datetime import datetime

connection_string = 'udp:127.0.0.1:10560'

print("connecting to link "+ connection_string)
# Connect to the Vehicle (in this case a UDP endpoint)
vehicle = connect(connection_string, wait_ready=True)
print("connection Successful")


#message raw cmd
#message: RC_CHANNELS {time_boot_ms : 1924818, chancount : 0, chan1_raw : 1472, chan2_raw : 1587, chan3_raw : 1493, chan4_raw : 1497, chan5_raw : 0, chan6_raw : 1000, chan7_raw : 0, chan8_raw : 0, chan9_raw : 0, chan10_raw : 0, chan11_raw : 0, chan12_raw : 0, chan13_raw : 0, chan14_raw : 0, chan15_raw : 0, chan16_raw : 0, chan17_raw : 0, chan18_raw : 0, rssi : 255}

def cur_usec():
    """Return current time in usecs"""
    # t = time.time()
    dt = datetime.now()
    t = dt.minute * 60 + dt.second + dt.microsecond / (1e6)
    return t
class MeasureTime(object):
    def __init__(self):
        self.prevtime = cur_usec()
        self.previnterval = 0
        self.numcount = 0
        self.reset()

    def reset(self):
        self.maxinterval = 0
        self.mininterval = 10000
        
    def log(self):
        #print "Interval", self.previnterval
        #print "MaxInterval", self.maxinterval
        #print "MinInterval", self.mininterval
        sys.stdout.write('MaxInterval: %s\tMinInterval: %s\tInterval: %s\r' % (self.maxinterval,self.mininterval, self.previnterval) )
        sys.stdout.flush()


    def update(self):
        now = cur_usec()
        self.numcount = self.numcount + 1
        self.previnterval = now - self.prevtime
        self.prevtime = now
        if self.numcount>1: #ignore first value where self.prevtime not reliable.
            self.maxinterval = max(self.previnterval, self.maxinterval)
            self.mininterval = min(self.mininterval, self.previnterval)
            self.log()

acktime = MeasureTime()

#Create COMMAND_ACK message listener.
@vehicle.on_message('RC_CHANNELS')
def listener(self, name, message):
    acktime.update()
    # send_testpackets()

def send_testpackets():
    #Send message using `command_long_encode` (returns an ACK)
    msg = vehicle.message_factory.command_long_encode(
                                                    1, 1,    # target system, target component
                                                    #mavutil.mavlink.MAV_CMD_DO_SET_RELAY, #command
                                                    mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
                                                    0, #confirmation
                                                    0, 0, 0, 0, #params 1-4
                                                    0,
                                                    0,
                                                    0
                                                    )

    vehicle.send_mavlink(msg)

#Start logging by sending a test packet
send_testpackets()

vehicle.close()
# if __name__ == "__main__":
#     try:
#         print("Main Execution begin...")
#         while True:
#             @vehicle.on_message('RC_CHANNELS')
#             def listener(self, name, message):
#                 print 'message: %s' % message.chan3_raw
#         else:
#             print("module loaded")
    
#     except KeyboardInterrupt:
#         vehicle.close()
#         sys.exit()