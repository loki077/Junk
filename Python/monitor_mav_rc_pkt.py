# Import mavutil
from pymavlink import mavutil
import time

def wait_conn():
    """
    Sends a ping to stabilish the UDP communication and awaits for a response
    """
    msg = None
    print("Send Mav Ping ")
    while not msg:
        msrc.mav.ping_send(
            int(time.time() * 1e6), # Unix time in microseconds
            0, # Ping number
            0, # Request ping of all systems
            0 # Request ping of all components
        )
        msg = msrc.recv_match()
        time.sleep(0.5)

# Create the connection to the top-side computer as companion computer/autopilot
msrc = mavutil.mavlink_connection('udpin:localhost:10560', source_system=1)

wait_conn()
print("Mavlink connection to  Successfull")
# Send a message for QGC to read out loud
#  Severity from https://mavlink.io/en/messages/common.html#MAV_SEVERITY
msrc.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_NOTICE,
                           "QGC will read this".encode())

while True:
    time.sleep(0.01)
    try:
        message = msrc.recv_match(type='RC_CHANNELS_OVERRIDE', blocking=True).to_dict()
        print(message)
    except Exception as error:
        print(error)
        sys.exit(0)