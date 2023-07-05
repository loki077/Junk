import os
from pymavlink import mavutil
import struct

# Define constants
GPS_FIX_TYPE = 3  # GPS fix type value indicating a 3D fix
MAX_NSATS = 20  # Maximum NSats value to reach

def gps_statistics(log_file, gps_lst_0 ,gps_lst_1):
    if(len(gps_lst_0) > 0 and len(gps_lst_0) > 0):
        gps_0_maximum = max(gps_lst_0)
        gps_0_minimum = min(gps_lst_0)
        gps_0_average = int(sum(gps_lst_0) / len(gps_lst_0))
        gps_1_maximum = max(gps_lst_1)
        gps_1_minimum = min(gps_lst_1)
        gps_1_average = int(sum(gps_lst_1) / len(gps_lst_1))
        log_file = log_file.replace('C:\\Users\\Lokesh\\Dropbox (Carbonix Company)\\Carbonix Engineering Team Folder\\Flight\\Flight Logs', '')
        print(log_file + ",GPS0," + str(gps_0_maximum) + "," + str(gps_0_minimum) + "," + str(gps_0_average) + ",GPS1," + str(gps_1_maximum) + "," + str(gps_1_minimum) + "," + str(gps_1_average))
    else:
        print(log_file + "," + "No GPS data found")

def extract_and_parse_logs(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.BIN'):
                log_path = os.path.join(root, file)
                # print(f"Processing: {log_path}")

                # Open the log file
                try:
                    log = mavutil.mavlink_connection(log_path)
                except:
                    print(f"Error opening log file: {log_path}")
                    continue
                
                msg_types = set(['GPS', "GPS2"])
                gps_0_data = []
                gps_1_data = []
                # Process the log messages
                while True:
                    msg = log.recv_match(type=msg_types)
                    if msg is None:
                        break
                    mtype = msg.get_type()
                    if msg.I == 0:
                        gps_0_data.append(msg.NSats)
                    if msg.I == 1:
                        gps_1_data.append(msg.NSats)
                gps_statistics(log_path, gps_0_data, gps_1_data)

# logs_folder_path = 'D:\\Logs\\V34'
logs_folder_path = 'C:\\Users\\Lokesh\\Dropbox (Carbonix Company)\\Carbonix Engineering Team Folder\\Flight\\Flight Logs\\V37'
extract_and_parse_logs(logs_folder_path)

print("Script End")


